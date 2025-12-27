import json
import re


def parse_questions_from_file(filename):
    """从文件解析题目"""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # 按题目编号分割
    # 使用正则表达式找到所有题目
    pattern = r'(\d+)[．\.]\s*(.+?)\s*A[．\.]\s*(.+?)\s*B[．\.]\s*(.+?)\s*C[．\.]\s*(.+?)\s*D[．\.]\s*(.+?)\s*答案[：:;]\s*([A-D])\s*解析[：:;]\s*(.+?)(?=\s*\d+[．\.]|$)'

    # 由于题目格式不规则，我们采用逐行解析的方法
    lines = [line.strip() for line in content.split('\n') if line.strip()]

    questions = []
    current_question = None
    collecting_options = False
    collecting_explanation = False
    option_index = 0

    for line in lines:
        # 跳过标题行
        if "练习题" in line:
            continue

        # 检测新题目开始
        match = re.match(r'^(\d+)[．\.]\s*(.*)', line)
        if match:
            if current_question:
                questions.append(current_question)

            current_question = {
                'number': match.group(1),
                'text': match.group(2),
                'options': [],
                'answer': '',
                'explanation': ''
            }
            collecting_options = False
            collecting_explanation = False
            option_index = 0
            continue

        # 检测选项
        if current_question and (line.startswith('A.') or line.startswith('A．') or
                                 line.startswith('B.') or line.startswith('B．') or
                                 line.startswith('C.') or line.startswith('C．') or
                                 line.startswith('D.') or line.startswith('D．')):
            collecting_options = True
            collecting_explanation = False

            # 提取选项文本
            option_match = re.match(r'^[A-D][．\.]\s*(.*)', line)
            if option_match:
                current_question['options'].append(option_match.group(1))
            continue

        # 检测答案
        if current_question and ('答案' in line):
            collecting_options = False
            collecting_explanation = False

            # 提取答案
            if '：' in line:
                answer = line.split('：', 1)[1].strip()
            elif ':' in line:
                answer = line.split(':', 1)[1].strip()
            elif ';' in line:
                answer = line.split(';', 1)[1].strip()
            else:
                answer = line.replace('答案', '').strip()

            current_question['answer'] = answer
            continue

        # 检测解析
        if current_question and ('解析' in line):
            collecting_options = False
            collecting_explanation = True

            # 提取解析
            if '：' in line:
                explanation = line.split('：', 1)[1].strip()
            elif ':' in line:
                explanation = line.split(':', 1)[1].strip()
            elif ';' in line:
                explanation = line.split(';', 1)[1].strip()
            else:
                explanation = line.replace('解析', '').strip()

            current_question['explanation'] = explanation
            continue

        # 如果是当前题目的文本
        if current_question:
            if collecting_explanation and current_question['explanation']:
                # 解析的续行
                current_question['explanation'] += ' ' + line
            elif not collecting_options and not current_question['answer']:
                # 题目文本的续行
                current_question['text'] += ' ' + line

    # 添加最后一个题目
    if current_question:
        questions.append(current_question)

    return questions


def save_questions_to_json(questions, output_file):
    """保存题目到JSON文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

    print(f"已保存 {len(questions)} 道题目到 {output_file}")

    # 显示前3题详情
    print("\n前3题详情:")
    for i, q in enumerate(questions[:3]):
        print(f"\n第{q['number']}题:")
        print(f"  题目: {q['text']}")
        print(f"  选项A: {q['options'][0] if len(q['options']) > 0 else '无'}")
        print(f"  选项B: {q['options'][1] if len(q['options']) > 1 else '无'}")
        print(f"  选项C: {q['options'][2] if len(q['options']) > 2 else '无'}")
        print(f"  选项D: {q['options'][3] if len(q['options']) > 3 else '无'}")
        print(f"  答案: {q['answer']}")
        print(f"  解析: {q['explanation']}")

    return questions


if __name__ == "__main__":
    input_file = "6练习题六卷.txt"
    output_file = "6练习题六卷.json"

    questions = parse_questions_from_file(input_file)
    save_questions_to_json(questions, output_file)