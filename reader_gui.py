#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zotero AI Reader — 图形界面入口

在界面中编辑配置、提示词与标签后调用 reader.main()。
依赖同目录下的 reader.py、config_loader.py。
"""

from __future__ import annotations

import importlib.util
import os
import queue
import sys
import threading
import traceback
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from typing import Optional


def _script_dir() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def resolve_default_config_path() -> Optional[str]:
    try:
        from config_loader import find_config_file

        p = find_config_file()
        if p and os.path.isfile(p):
            return p
    except Exception:
        pass
    base = _script_dir()
    d = base
    for _ in range(6):
        cand = os.path.join(d, "zotero_ai_read_config.py")
        if os.path.isfile(cand):
            return cand
        nd = os.path.dirname(d)
        if nd == d:
            break
        d = nd
    for c in (os.path.join(base, "config.py"), os.path.join(base, "zotero_ai_read_config.py")):
        if os.path.isfile(c):
            return c
    return None


def load_config_module(path: str):
    spec = importlib.util.spec_from_file_location("gui_zotero_config", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("无法加载配置文件")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _as_str(v) -> str:
    if v is None:
        return ""
    return str(v)


def _parse_item_types(text: str):
    t = text.strip()
    if not t:
        return None
    return [p.strip() for p in t.split(",") if p.strip()]


def _format_item_types(val) -> str:
    if val is None:
        return ""
    if isinstance(val, (list, tuple)):
        return ", ".join(str(x) for x in val)
    return str(val)


def _format_keep_tags(val) -> str:
    if val is None:
        return ""
    if isinstance(val, (list, tuple)):
        return ", ".join(str(x) for x in val)
    return str(val)


    return str(val)
    

def resolve_dynamic_path(path: str) -> str:
    """解析动态路径占位符
    - {{mmdd}} -> 当前月日 (如 0419)
    - 0-New/mmdd -> 0-New/0419
    """
    if not path:
        return path
    
    # 使用本地时间
    mmdd = datetime.datetime.now().strftime('%m%d')
    
    # 1. 替换通用占位符
    resolved = path.replace('{{mmdd}}', mmdd)
    
    # 2. 特殊处理：如果路径恰好是 "0-New/mmdd" (用户习惯)
    if resolved == '0-New/mmdd':
        resolved = f'0-New/{mmdd}'
        
    return resolved


class QueueWriter:
    def __init__(self, q: queue.Queue, kind: str):
        self.q = q
        self.kind = kind

    def write(self, s: str) -> int:
        if s:
            self.q.put((self.kind, s))
        return len(s) if s else 0

    def flush(self) -> None:
        pass


class ReaderGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Zotero AI Reader — 图形界面")
        self.geometry("1100x780")
        self.minsize(880, 560)

        self._log_queue: queue.Queue = queue.Queue()
        self._run_thread: Optional[threading.Thread] = None
        self._busy = False

        self._build_ui()
        default = resolve_default_config_path()
        if default:
            self.var_config_path.set(default)
            self.after(100, lambda: self.load_config_from_path(default, show_ok=False))

    def _build_ui(self) -> None:
        top = ttk.Frame(self, padding=6)
        top.pack(fill=tk.X)
        ttk.Label(top, text="配置文件 (.py):").pack(side=tk.LEFT)
        self.var_config_path = tk.StringVar()
        ttk.Entry(top, textvariable=self.var_config_path, width=72).pack(
            side=tk.LEFT, padx=4, fill=tk.X, expand=True
        )
        ttk.Button(top, text="浏览…", command=self.browse_config).pack(side=tk.LEFT)
        ttk.Button(top, text="加载配置", command=self.on_load_config).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="重载提示词文件", command=self.reload_prompt_file).pack(side=tk.LEFT)

        paned = ttk.Panedwindow(self, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        nb = ttk.Notebook(paned)
        paned.add(nb, weight=3)

        # —— Zotero ——
        tab_z = ttk.Frame(nb, padding=8)
        nb.add(tab_z, text="Zotero")
        r = 0
        self.var_library_id = tk.StringVar()
        self.var_api_key = tk.StringVar()
        self.var_library_type = tk.StringVar(value="user")
        self.var_storage = tk.StringVar()
        for lab, var, show in (
            ("库 ID (LIBRARY_ID)", self.var_library_id, None),
            ("API Key (读写)", self.var_api_key, "*"),
            ("库类型", self.var_library_type, None),
            ("本地 PDF 目录 (ZOTERO_STORAGE_PATH)", self.var_storage, None),
        ):
            ttk.Label(tab_z, text=lab).grid(row=r, column=0, sticky=tk.W, pady=2)
            if lab.startswith("库类型"):
                cb = ttk.Combobox(
                    tab_z,
                    textvariable=self.var_library_type,
                    values=("user", "group"),
                    width=58,
                    state="readonly",
                )
                cb.grid(row=r, column=1, sticky=tk.EW, pady=2)
            else:
                ent = ttk.Entry(tab_z, textvariable=var, width=62)
                if show:
                    ent.configure(show=show)
                ent.grid(row=r, column=1, sticky=tk.EW, pady=2)
            r += 1
        ttk.Button(tab_z, text="浏览文件夹…", command=self.browse_storage).grid(
            row=r, column=1, sticky=tk.E, pady=4
        )
        tab_z.columnconfigure(1, weight=1)

        # —— AI ——
        tab_ai = ttk.Frame(nb, padding=8)
        nb.add(tab_ai, text="AI 模型")
        self.var_ai_provider = tk.StringVar(value="gemini")
        ttk.Label(tab_ai, text="本次运行使用的提供商").grid(row=0, column=0, sticky=tk.W)
        frp = ttk.Frame(tab_ai)
        frp.grid(row=0, column=1, sticky=tk.W)
        ttk.Radiobutton(frp, text="Google Gemini", variable=self.var_ai_provider, value="gemini").pack(
            side=tk.LEFT, padx=4
        )
        ttk.Radiobutton(frp, text="小米 MIMO", variable=self.var_ai_provider, value="xiaomi").pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(frp, text="按提供商填入默认标签", command=self.apply_default_tags_for_provider).pack(
            side=tk.LEFT, padx=12
        )

        self.var_gemini_key = tk.StringVar()
        self.var_gemini_model = tk.StringVar()
        self.var_xiaomi_key = tk.StringVar()
        self.var_xiaomi_model = tk.StringVar()
        r = 1
        for lab, var in (
            ("Gemini API Key", self.var_gemini_key),
            ("Gemini 模型 (AI_MODEL)", self.var_gemini_model),
            ("小米 API Key", self.var_xiaomi_key),
            ("小米模型 (XIAOMI_MODEL)", self.var_xiaomi_model),
        ):
            ttk.Label(tab_ai, text=lab).grid(row=r, column=0, sticky=tk.W, pady=2)
            ent = ttk.Entry(tab_ai, textvariable=var, width=62)
            if "Key" in lab:
                ent.configure(show="*")
            ent.grid(row=r, column=1, sticky=tk.EW, pady=2)
            r += 1
        tab_ai.columnconfigure(1, weight=1)

        # —— 处理范围 ——
        tab_proc = ttk.Frame(nb, padding=8)
        nb.add(tab_proc, text="处理范围")
        self.var_target_collection = tk.StringVar()
        self.var_item_types = tk.StringVar()
        self.var_prompt_filename = tk.StringVar(value="prompt.md")
        self.var_test_mode = tk.BooleanVar(value=False)
        self.var_test_limit = tk.StringVar(value="3")
        r = 0
        ttk.Label(tab_proc, text="目标集合路径 (TARGET_COLLECTION_PATH，空=整库)").grid(
            row=r, column=0, sticky=tk.NW, pady=2
        )
        ttk.Entry(tab_proc, textvariable=self.var_target_collection, width=62).grid(
            row=r, column=1, sticky=tk.EW, pady=2
        )
        r += 1
        ttk.Label(
            tab_proc,
            text="文献类型过滤 (ITEM_TYPES_TO_PROCESS，逗号分隔，空=全部)",
        ).grid(row=r, column=0, sticky=tk.NW, pady=2)
        ttk.Entry(tab_proc, textvariable=self.var_item_types, width=62).grid(
            row=r, column=1, sticky=tk.EW, pady=2
        )
        r += 1
        ttk.Label(tab_proc, text="提示词文件名 (写入笔记页脚)").grid(row=r, column=0, sticky=tk.W, pady=2)
        ttk.Entry(tab_proc, textvariable=self.var_prompt_filename, width=62).grid(
            row=r, column=1, sticky=tk.EW, pady=2
        )
        r += 1
        ttk.Checkbutton(tab_proc, text="测试模式 (TEST_MODE)", variable=self.var_test_mode).grid(
            row=r, column=1, sticky=tk.W, pady=2
        )
        r += 1
        ttk.Label(tab_proc, text="测试条数 (TEST_LIMIT)").grid(row=r, column=0, sticky=tk.W, pady=2)
        ttk.Entry(tab_proc, textvariable=self.var_test_limit, width=12).grid(
            row=r, column=1, sticky=tk.W, pady=2
        )
        tab_proc.columnconfigure(1, weight=1)

        # —— 标签 ——
        tab_tags = ttk.Frame(nb, padding=8)
        nb.add(tab_tags, text="标签")
        self.var_success_tag = tk.StringVar()
        self.var_non_lit_tag = tk.StringVar()
        self.var_tags_skip = tk.StringVar(value="gemini_read, MIMO_read")
        self.var_keep_tags = tk.StringVar()
        r = 0
        for lab, var in (
            ("成功后打在条目上的标签 (SUCCESS_TAG)", self.var_success_tag),
            ("跳过/非文献时使用的标签 (NON_LIT_TAG)", self.var_non_lit_tag),
            ("视为「已处理」的标签，逗号分隔 (跳过这些条目)", self.var_tags_skip),
            ("保留标签参考 (KEEP_TAGS，当前 reader 不写入，仅备忘)", self.var_keep_tags),
        ):
            ttk.Label(tab_tags, text=lab).grid(row=r, column=0, sticky=tk.NW, pady=2)
            ttk.Entry(tab_tags, textvariable=var, width=62).grid(
                row=r, column=1, sticky=tk.EW, pady=2
            )
            r += 1
        tab_tags.columnconfigure(1, weight=1)

        # —— 提示词 ——
        tab_prompt = ttk.Frame(nb, padding=4)
        nb.add(tab_prompt, text="提示词")

        # 提示词展示区
        desc_bar = ttk.Frame(tab_prompt)
        desc_bar.pack(fill=tk.X, padx=4, pady=(4, 0))
        ttk.Label(desc_bar, text="当前提示词内容 (可在下方直接编辑)：", foreground="gray").pack(side=tk.LEFT)

        self.txt_prompt = scrolledtext.ScrolledText(tab_prompt, height=18, wrap=tk.WORD, font=("Consolas", 10))
        self.txt_prompt.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        pf = ttk.Frame(tab_prompt)
        pf.pack(fill=tk.X, padx=4, pady=4)
        ttk.Button(pf, text="保存提示词到文件", command=self.save_prompt_to_file).pack(side=tk.LEFT)

        # —— 运行 + 日志 ——
        bar = ttk.Frame(paned, padding=4)
        paned.add(bar, weight=0)
        ttk.Button(bar, text="开始运行", command=self.on_run).pack(side=tk.LEFT, padx=2)
        ttk.Label(bar, text="运行中请勿关闭窗口；日志见下方。").pack(side=tk.LEFT, padx=12)

        log_frame = ttk.Frame(paned, padding=4)
        paned.add(log_frame, weight=2)
        self.txt_log = scrolledtext.ScrolledText(log_frame, height=14, wrap=tk.WORD, state=tk.DISABLED)
        self.txt_log.pack(fill=tk.BOTH, expand=True)

        self.after(200, self._drain_log_queue)

    def browse_config(self) -> None:
        p = filedialog.askopenfilename(
            title="选择配置文件",
            filetypes=[("Python", "*.py"), ("所有文件", "*.*")],
            initialdir=_script_dir(),
        )
        if p:
            self.var_config_path.set(p)

    def browse_storage(self) -> None:
        p = filedialog.askdirectory(title="选择 Zotero PDF 目录")
        if p:
            self.var_storage.set(p)

    def on_load_config(self) -> None:
        p = self.var_config_path.get().strip()
        if not p:
            messagebox.showwarning("提示", "请先选择配置文件路径。")
            return
        self.load_config_from_path(p, show_ok=True)

    def load_config_from_path(self, path: str, show_ok: bool) -> None:
        try:
            mod = load_config_module(path)
        except Exception as e:
            messagebox.showerror("加载失败", str(e))
            return

        self.var_library_id.set(_as_str(getattr(mod, "LIBRARY_ID", "")))
        self.var_api_key.set(_as_str(getattr(mod, "API_KEY", "")))
        self.var_library_type.set(_as_str(getattr(mod, "LIBRARY_TYPE", "user")) or "user")
        self.var_storage.set(_as_str(getattr(mod, "ZOTERO_STORAGE_PATH", "")))

        self.var_gemini_key.set(_as_str(getattr(mod, "AI_API_KEY", "")))
        self.var_gemini_model.set(
            _as_str(getattr(mod, "AI_MODEL", "gemini-3.1-flash-lite-preview"))
        )
        self.var_xiaomi_key.set(_as_str(getattr(mod, "XiaoMi_API_KEY", "")))
        self.var_xiaomi_model.set(_as_str(getattr(mod, "XIAOMI_MODEL", "mimo-v2-pro")))
        self._xiaomi_base_url = getattr(mod, "MIMO_BASE_URL", getattr(mod, "XIAOMI_BASE_URL", None))

        def_prov = getattr(mod, "DEFAULT_AI_PROVIDER", None)
        if def_prov in ("gemini", "xiaomi"):
            self.var_ai_provider.set(def_prov)
        else:
            self.var_ai_provider.set("gemini")

        self.var_prompt_filename.set(_as_str(getattr(mod, "PROMPT_FILE_NAME", "prompt.md")) or "prompt.md")
        self.var_item_types.set(_format_item_types(getattr(mod, "ITEM_TYPES_TO_PROCESS", None)))
        tc = getattr(mod, "TARGET_COLLECTION_PATH", None)
        # 解析动态路径
        tc_resolved = resolve_dynamic_path("" if tc is None else _as_str(tc))
        self.var_target_collection.set(tc_resolved)
        self.var_test_mode.set(bool(getattr(mod, "TEST_MODE", False)))
        self.var_test_limit.set(_as_str(getattr(mod, "TEST_LIMIT", 3)))

        self.var_keep_tags.set(_format_keep_tags(getattr(mod, "KEEP_TAGS", [])))
        self.apply_default_tags_for_provider(silent=True)

        self.reload_prompt_file(silent=True)
        if show_ok:
            messagebox.showinfo("完成", "已从配置文件填充各字段（提示词已从文件读取）。")

    def apply_default_tags_for_provider(self, silent: bool = False) -> None:
        if self.var_ai_provider.get() == "gemini":
            self.var_success_tag.set("gemini_read")
            self.var_non_lit_tag.set("non-read-gemini")
        else:
            self.var_success_tag.set("MIMO_read")
            self.var_non_lit_tag.set("non-read-mimo")
        if not silent:
            messagebox.showinfo("标签", "已根据当前 AI 提供商填入默认成功/跳过标签。")


    def reload_prompt_file(self, silent: bool = False) -> None:
        name = self.var_prompt_filename.get().strip() or "prompt.md"
        fp = os.path.join(_script_dir(), name)
        if not os.path.isfile(fp):
            if not silent:
                messagebox.showwarning("提示词", f"未找到文件:\n{fp}")
            return
        try:
            with open(fp, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            if not silent:
                messagebox.showerror("读取失败", str(e))
            return
        self.txt_prompt.delete("1.0", tk.END)
        self.txt_prompt.insert("1.0", text)
        if not silent:
            messagebox.showinfo("提示词", f"已加载: {name}")

    def save_prompt_to_file(self) -> None:
        name = self.var_prompt_filename.get().strip() or "prompt.md"
        fp = os.path.join(_script_dir(), name)
        try:
            body = self.txt_prompt.get("1.0", tk.END)
            with open(fp, "w", encoding="utf-8") as f:
                f.write(body)
        except Exception as e:
            messagebox.showerror("保存失败", str(e))
            return
        messagebox.showinfo("保存", f"已写入:\n{fp}")

    def _append_log(self, s: str) -> None:
        self.txt_log.configure(state=tk.NORMAL)
        self.txt_log.insert(tk.END, s)
        self.txt_log.see(tk.END)
        self.txt_log.configure(state=tk.DISABLED)

    def _drain_log_queue(self) -> None:
        try:
            while True:
                item = self._log_queue.get_nowait()
                if isinstance(item, tuple) and len(item) == 2 and item[0] == "done":
                    self._busy = False
                    self._append_log("\n======== 任务结束 ========\n")
                    continue
                if isinstance(item, tuple) and len(item) == 2:
                    _, chunk = item
                    self._append_log(chunk)
                else:
                    self._append_log(str(item))
        except queue.Empty:
            pass
        self.after(120, self._drain_log_queue)

    def _validate_before_run(self) -> bool:
        if not self.var_library_id.get().strip():
            messagebox.showerror("校验", "请填写 LIBRARY_ID。")
            return False
        if not self.var_api_key.get().strip():
            messagebox.showerror("校验", "请填写 Zotero API_KEY。")
            return False
        if not self.var_storage.get().strip():
            messagebox.showerror("校验", "请填写本地 PDF 目录。")
            return False
        prov = self.var_ai_provider.get()
        if prov == "gemini" and not self.var_gemini_key.get().strip():
            messagebox.showerror("校验", "使用 Gemini 时请填写 Gemini API Key。")
            return False
        if prov == "xiaomi" and not self.var_xiaomi_key.get().strip():
            messagebox.showerror("校验", "使用小米时请填写小米 API Key。")
            return False
        prompt = self.txt_prompt.get("1.0", tk.END).strip()
        if not prompt:
            messagebox.showerror("校验", "提示词内容为空。")
            return False
        try:
            int(self.var_test_limit.get().strip() or "3")
        except ValueError:
            messagebox.showerror("校验", "TEST_LIMIT 必须是整数。")
            return False
        return True

    def on_run(self) -> None:
        if self._busy:
            messagebox.showinfo("提示", "任务正在运行中。")
            return
        if not self._validate_before_run():
            return

        prov = self.var_ai_provider.get()
        if prov == "gemini":
            active_key = self.var_gemini_key.get().strip()
            active_model = self.var_gemini_model.get().strip() or "gemini-3.1-flash-lite-preview"
        else:
            active_key = self.var_xiaomi_key.get().strip()
            active_model = self.var_xiaomi_model.get().strip() or "mimo-v2-pro"

        tc = self.var_target_collection.get().strip()
        target_path = tc if tc else None

        try:
            test_limit = int(self.var_test_limit.get().strip() or "3")
        except ValueError:
            test_limit = 3

        item_types = _parse_item_types(self.var_item_types.get())
        tags_skip = self.var_tags_skip.get().strip()

        payload = {
            "library_id": self.var_library_id.get().strip(),
            "api_key": self.var_api_key.get().strip(),
            "library_type": self.var_library_type.get().strip() or "user",
            "zotero_storage_path": self.var_storage.get().strip(),
            "ai_provider": prov,
            "active_api_key": active_key,
            "active_model": active_model,
            "prompt_file_name": self.var_prompt_filename.get().strip() or "prompt.md",
            "prompt_template": self.txt_prompt.get("1.0", tk.END),
            "item_types_to_process": item_types,
            "target_collection_path": target_path,
            "test_mode": self.var_test_mode.get(),
            "test_limit": test_limit,
            "success_tag": self.var_success_tag.get().strip() or "gemini_read",
            "non_lit_tag": self.var_non_lit_tag.get().strip() or "non-read-gemini",
            "tags_skip_if_present": tags_skip if tags_skip else None,
            "xiaomi_base_url": getattr(self, "_xiaomi_base_url", None),
        }

        self._busy = True
        self._append_log("\n======== 任务开始 ========\n")

        def job():
            old_out, old_err = sys.stdout, sys.stderr
            sys.stdout = QueueWriter(self._log_queue, "out")
            sys.stderr = QueueWriter(self._log_queue, "err")
            try:
                import reader as reader_mod

                reader_mod.apply_gui_settings(**payload)
                reader_mod.main()
            except Exception:
                self._log_queue.put(("err", traceback.format_exc()))
            finally:
                sys.stdout = old_out
                sys.stderr = old_err
                self._log_queue.put(("done", None))

        self._run_thread = threading.Thread(target=job, daemon=True)
        self._run_thread.start()


def main():
    app = ReaderGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
