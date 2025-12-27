# quiz_system.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import random
import os
from datetime import datetime


class QuizSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("信息安全练习题答题系统")
        self.root.geometry("1000x700")

        # 数据存储
        self.questions = []
        self.wrong_questions = []
        self.current_index = 0
        self.total_questions = 0
        self.correct_count = 0
        self.answered_count = 0
        self.random_mode = False
        self.question_order = []

        # 界面颜色
        self.colors = {
            'bg': '#f0f0f0',
            'question_bg': '#ffffff',
            'button_bg': '#4CAF50',
            'button_fg': '#ffffff',
            'wrong_bg': '#ffebee',
            'correct_bg': '#e8f5e9'
        }

        # 创建主界面
        self.setup_ui()
        # 加载错题记录
        self.load_wrong_questions()

    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 控制面板
        control_frame = ttk.LabelFrame(main_frame, text="控制面板", padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))

        # 按钮
        ttk.Button(control_frame, text="加载题库", command=self.load_questions).grid(row=0, column=0, padx=5, pady=5,
                                                                                     sticky=tk.W)
        ttk.Button(control_frame, text="开始答题", command=self.start_quiz).grid(row=1, column=0, padx=5, pady=5,
                                                                                 sticky=tk.W)
        ttk.Button(control_frame, text="错题本", command=self.show_wrong_questions).grid(row=2, column=0, padx=5,
                                                                                         pady=5, sticky=tk.W)
        ttk.Button(control_frame, text="随机出题", command=self.toggle_random_mode).grid(row=3, column=0, padx=5,
                                                                                         pady=5, sticky=tk.W)
        ttk.Button(control_frame, text="统计信息", command=self.show_stats).grid(row=4, column=0, padx=5, pady=5,
                                                                                 sticky=tk.W)

        # 随机模式显示
        self.random_label = ttk.Label(control_frame, text="顺序模式", foreground="blue")
        self.random_label.grid(row=5, column=0, padx=5, pady=(10, 5), sticky=tk.W)

        # 统计信息显示
        stats_frame = ttk.Frame(control_frame)
        stats_frame.grid(row=6, column=0, pady=(10, 0))

        self.stats_label = ttk.Label(stats_frame, text="")
        self.stats_label.pack()

        # 答题区域
        quiz_frame = ttk.LabelFrame(main_frame, text="答题区域", padding="10")
        quiz_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 题目编号和进度
        progress_frame = ttk.Frame(quiz_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 10))

        self.question_label = ttk.Label(progress_frame, text="题目: 0/0", font=('Arial', 12))
        self.question_label.pack(side=tk.LEFT)

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))

        # 题目文本
        question_text_frame = ttk.Frame(quiz_frame)
        question_text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.question_text = tk.Text(question_text_frame, wrap=tk.WORD, height=6,
                                     font=('Microsoft YaHei', 11), bg=self.colors['question_bg'])
        self.question_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(question_text_frame, command=self.question_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.question_text.config(yscrollcommand=scrollbar.set)

        # 选项按钮框架
        self.options_frame = ttk.LabelFrame(quiz_frame, text="请选择答案")
        self.options_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 创建选项按钮 - 修改这里
        self.option_buttons = []
        option_labels = ['A', 'B', 'C', 'D']

        for i, label in enumerate(option_labels):
            btn = tk.Button(self.options_frame, text=f"{label}. ", font=('Arial', 12, 'bold'),
                            bg='#e0e0e0', fg='black', height=2, anchor='w',
                            command=lambda t=label: self.select_option(t))
            btn.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.option_buttons.append(btn)

        # 导航按钮
        nav_frame = ttk.Frame(quiz_frame)
        nav_frame.pack(fill=tk.X)

        ttk.Button(nav_frame, text="上一题", command=self.prev_question).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="下一题", command=self.next_question).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="提交答案", command=self.submit_answer).pack(side=tk.LEFT, padx=5)

        # 答案解析区域
        self.answer_frame = ttk.LabelFrame(quiz_frame, text="答案解析")
        self.answer_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        self.answer_text = tk.Text(self.answer_frame, wrap=tk.WORD, height=4,
                                   font=('Microsoft YaHei', 10), bg=self.colors['question_bg'])
        self.answer_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar2 = ttk.Scrollbar(self.answer_frame, command=self.answer_text.yview)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        self.answer_text.config(yscrollcommand=scrollbar2.set)

    def load_questions(self):
        """加载题库"""
        file_path = filedialog.askopenfilename(
            title="选择题库文件",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")]
        )

        if file_path:
            try:
                if file_path.endswith('.json'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.questions = json.load(f)
                elif file_path.endswith('.txt'):
                    # 如果是文本文件，调用转换器
                    from converter import TextToJsonConverter
                    converter = TextToJsonConverter()
                    self.questions = converter.convert_file(file_path)

                    # 保存为JSON
                    json_path = file_path.replace('.txt', '.json')
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(self.questions, f, ensure_ascii=False, indent=2)
                    messagebox.showinfo("转换完成", f"题目已转换为JSON格式并保存到:\n{json_path}")
                else:
                    messagebox.showerror("错误", "不支持的文件格式")
                    return

                self.total_questions = len(self.questions)
                self.current_index = 0
                self.reset_quiz_state()
                self.update_question_display()
                messagebox.showinfo("加载成功", f"成功加载 {self.total_questions} 道题目")

            except Exception as e:
                messagebox.showerror("加载失败", f"加载题库时出错:\n{str(e)}")

    def reset_quiz_state(self):
        """重置答题状态"""
        self.correct_count = 0
        self.answered_count = 0
        self.question_order = list(range(self.total_questions))

        # 为每道题目添加答题状态
        for q in self.questions:
            q['answered'] = False
            q['user_answer'] = None
            q['is_correct'] = False

    def update_question_display(self):
        """更新题目显示"""
        if not self.questions or self.total_questions == 0:
            return

        # 获取当前题目
        if self.random_mode and self.question_order:
            actual_index = self.question_order[self.current_index]
        else:
            actual_index = self.current_index

        question = self.questions[actual_index]

        # 更新进度
        self.question_label.config(text=f"题目: {self.current_index + 1}/{self.total_questions}")
        self.progress_var.set((self.current_index + 1) / self.total_questions * 100)

        # 显示题目
        self.question_text.delete(1.0, tk.END)
        self.question_text.insert(1.0, f"{question.get('number', '')}. {question.get('text', '')}")

        # 显示选项 - 修改这里
        for i, btn in enumerate(self.option_buttons):
            option_text = question.get('options', [''])[i] if i < len(question.get('options', [])) else ""
            btn.config(text=f"{chr(65 + i)}. {option_text}")  # 显示 A. 选项内容

            # 根据答题状态设置按钮颜色
            if question['answered']:
                if question['user_answer'] == chr(65 + i):  # 'A', 'B', 'C', 'D'
                    if question['is_correct']:
                        btn.config(bg=self.colors['correct_bg'])
                    else:
                        btn.config(bg=self.colors['wrong_bg'])
                elif question.get('answer', '') == chr(65 + i):
                    btn.config(bg=self.colors['correct_bg'])
                else:
                    btn.config(bg='#e0e0e0')
            else:
                btn.config(bg='#e0e0e0')

        # 显示答案解析
        self.answer_text.delete(1.0, tk.END)
        if question['answered']:
            explanation = question.get('explanation', '无解析')
            self.answer_text.insert(1.0, f"你的答案: {question['user_answer']}\n")
            self.answer_text.insert(tk.END, f"正确答案: {question.get('answer', '')}\n")
            self.answer_text.insert(tk.END, f"解析: {explanation}")

        # 更新统计信息
        self.update_stats_display()

    def select_option(self, option):
        """选择选项"""
        if not self.questions:
            return

        if self.random_mode and self.question_order:
            actual_index = self.question_order[self.current_index]
        else:
            actual_index = self.current_index

        question = self.questions[actual_index]

        if not question['answered']:
            # 更新用户答案
            question['user_answer'] = option

            # 更新按钮颜色
            for i, btn in enumerate(self.option_buttons):
                if chr(65 + i) == option:
                    btn.config(bg='#bbdefb')  # 选中颜色
                else:
                    btn.config(bg='#e0e0e0')

    def submit_answer(self):
        """提交答案"""
        if not self.questions:
            return

        if self.random_mode and self.question_order:
            actual_index = self.question_order[self.current_index]
        else:
            actual_index = self.current_index

        question = self.questions[actual_index]

        if not question['user_answer']:
            messagebox.showwarning("提示", "请先选择一个答案")
            return

        # 检查答案
        user_answer = question['user_answer']
        correct_answer = question.get('answer', '')

        # 处理多选题（如"AB"、"AC"等）
        if len(correct_answer) > 1:
            is_correct = set(user_answer) == set(correct_answer)
        else:
            is_correct = user_answer == correct_answer

        question['is_correct'] = is_correct
        question['answered'] = True

        # 更新统计
        self.answered_count += 1
        if is_correct:
            self.correct_count += 1
        else:
            # 添加到错题本
            self.add_to_wrong_questions(question, user_answer)

        # 更新显示
        self.update_question_display()

    def add_to_wrong_questions(self, question, user_answer):
        """添加到错题本"""
        wrong_record = {
            'question': question.copy(),
            'user_answer': user_answer,
            'correct_answer': question.get('answer', ''),
            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # 避免重复添加相同的错题
        existing = False
        for record in self.wrong_questions:
            if record['question']['text'] == question['text']:
                existing = True
                break

        if not existing:
            self.wrong_questions.append(wrong_record)
            self.save_wrong_questions()

    def save_wrong_questions(self):
        """保存错题记录"""
        try:
            with open('wrong_questions.json', 'w', encoding='utf-8') as f:
                json.dump(self.wrong_questions, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存错题时出错: {e}")

    def load_wrong_questions(self):
        """加载错题记录"""
        try:
            if os.path.exists('wrong_questions.json'):
                with open('wrong_questions.json', 'r', encoding='utf-8') as f:
                    self.wrong_questions = json.load(f)
        except Exception as e:
            print(f"加载错题时出错: {e}")
            self.wrong_questions = []

    def show_wrong_questions(self):
        """显示错题本窗口"""
        if not self.wrong_questions:
            messagebox.showinfo("错题本", "暂无错题记录")
            return

        wrong_window = tk.Toplevel(self.root)
        wrong_window.title("错题本")
        wrong_window.geometry("800x600")

        # 创建文本框
        text_widget = tk.Text(wrong_window, wrap=tk.WORD, font=('Microsoft YaHei', 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(text_widget)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=text_widget.yview)

        # 显示错题
        for i, record in enumerate(self.wrong_questions):
            question = record['question']
            text_widget.insert(tk.END, f"{i + 1}. {question.get('text', '')}\n\n")

            # 显示选项
            for option in question.get('options', []):
                text_widget.insert(tk.END, f"  {option}\n")

            text_widget.insert(tk.END, f"\n你的答案: {record['user_answer']}\n")
            text_widget.insert(tk.END, f"正确答案: {record['correct_answer']}\n")
            text_widget.insert(tk.END, f"解析: {question.get('explanation', '无解析')}\n")
            text_widget.insert(tk.END, f"时间: {record['time']}\n")
            text_widget.insert(tk.END, "-" * 60 + "\n\n")

        text_widget.config(state=tk.DISABLED)  # 设置为只读

        # 清空错题按钮
        def clear_wrong_questions():
            if messagebox.askyesno("确认", "确定要清空所有错题记录吗？"):
                self.wrong_questions = []
                self.save_wrong_questions()
                wrong_window.destroy()
                messagebox.showinfo("提示", "错题记录已清空")

        ttk.Button(wrong_window, text="清空错题本", command=clear_wrong_questions).pack(pady=10)

    def toggle_random_mode(self):
        """切换随机出题模式"""
        self.random_mode = not self.random_mode

        if self.random_mode:
            self.random_label.config(text="随机模式", foreground="red")
            if self.questions:
                random.shuffle(self.question_order)
                self.current_index = 0
                self.update_question_display()
        else:
            self.random_label.config(text="顺序模式", foreground="blue")
            if self.questions:
                self.question_order = list(range(self.total_questions))
                self.current_index = 0
                self.update_question_display()

    def start_quiz(self):
        """开始答题"""
        if not self.questions:
            messagebox.showwarning("提示", "请先加载题库")
            return

        self.reset_quiz_state()
        self.current_index = 0

        if self.random_mode:
            random.shuffle(self.question_order)

        self.update_question_display()
        messagebox.showinfo("开始答题", f"开始答题，共 {self.total_questions} 道题")

    def next_question(self):
        """下一题"""
        if self.current_index < self.total_questions - 1:
            self.current_index += 1
            self.update_question_display()

    def prev_question(self):
        """上一题"""
        if self.current_index > 0:
            self.current_index -= 1
            self.update_question_display()

    def update_stats_display(self):
        """更新统计信息显示"""
        if self.total_questions > 0:
            accuracy = (self.correct_count / self.answered_count * 100) if self.answered_count > 0 else 0
            stats_text = f"正确: {self.correct_count}/{self.answered_count} ({accuracy:.1f}%)"
            self.stats_label.config(text=stats_text)

    def show_stats(self):
        """显示详细统计信息"""
        if not self.questions:
            messagebox.showinfo("统计", "暂无答题数据")
            return

        total_answered = sum(1 for q in self.questions if q['answered'])
        total_correct = sum(1 for q in self.questions if q.get('is_correct', False))

        accuracy = (total_correct / total_answered * 100) if total_answered > 0 else 0

        stats_text = f"""
        答题统计:
        ------------
        总题数: {self.total_questions}
        已答题数: {total_answered}
        正确题数: {total_correct}
        正确率: {accuracy:.1f}%
        错题数: {len(self.wrong_questions)}
        """

        messagebox.showinfo("答题统计", stats_text)


def main():
    root = tk.Tk()
    app = QuizSystem(root)
    root.mainloop()


if __name__ == "__main__":
    main()