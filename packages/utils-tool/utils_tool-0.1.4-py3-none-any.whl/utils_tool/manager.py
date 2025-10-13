"""开发支持工具 black path"""

import subprocess
import os

####
class GitHubManager:
    """
    一个用于管理和获取 GitHub 仓库提交历史的工具类。

    此类能够执行 Git 命令来获取指定 GitHub 仓库的提交历史，
    并将其格式化为 Mermaid Git Graph 语法，以便于可视化。
    主要用于获取仓库的 Git 记录，并可将这些记录用于其他目的。
    """

    def __init__(self):
        """
        初始化 GitHubManager 实例。

        设置 Mermaid 图的格式字符串。
        """
        self.mermaid_format = """
        ```mermaid
        {mermaid_code}
        ```
        """

    def _get_origin(self):
        """
        获取并推送指定 GitHub 仓库的 Git 记录。

        此方法遍历预定义的 GitHub 仓库列表，并对每个仓库执行 `git push origin main` 命令。
        主要用于确保本地仓库与远程主分支同步。

        注意:
            此方法包含硬编码的本地路径和仓库列表，可能需要根据实际环境进行调整。
            目前包含一个 TODO 标记，表示可能需要进一步完善。
        """
        home = "/Users/zhaoxuefeng/GitHub/"

        for repo in [
            "toolsz",
            "llmada",
            "clientz",
            "commender",
            "mermaidz",
            "kanbanz",
            "querypipz",
            "appscriptz",
            "reallife-client-mac",
            "designerz",
            "algorithmz",
            "reallife",
            "promptlibz",
        ]:
            os.system(f"git -C {os.path.join(home,repo)} push origin main")

    def generate_mermaid_git_graph(self, simulated_git_log: str) -> str:
        """
        将模拟的 Git 日志输出转换为 Mermaid Git Graph 语法。

        此方法解析 Git 日志的简化输出，并将其转换为 Mermaid 图所需的 `gitGraph` 格式。
        它能够识别提交哈希、分支引用和提交消息，并将其转换为 Mermaid 图的节点和标签。

        Args:
            simulated_git_log (str): 模拟的 Git 日志字符串，通常是 `git log --all --graph --pretty=format:%h,%d,%s` 的输出。

        Returns:
            str: 格式化为 Mermaid Git Graph 语法的字符串。
        """

        mermaid_code = "gitGraph\n"
        commits_seen = {}  # To track commits and avoid duplicates if needed

        for line in simulated_git_log.strip().split("\n"):
            line = line.strip()
            if line.startswith("*"):
                # Parse the commit line
                # Handle potential extra space after * and split by the first two commas
                parts = line[1:].strip().split(",", 2)
                if len(parts) >= 2:
                    hash_val = parts[0].strip()
                    refs = parts[1].strip()
                    message = parts[2].strip() if len(parts) > 2 else ""

                    commit_line = f'    commit id: "{hash_val}"'

                    # Process references (branches, tags)
                    if refs:
                        # Remove parentheses and split by comma
                        ref_list = [
                            r.strip()
                            for r in refs.replace("(", "").replace(")", "").split(",")
                            if r.strip()
                        ]
                        processed_refs = []
                        for ref in ref_list:
                            if "->" in ref:
                                ref = ref.split("->")[
                                    -1
                                ].strip()  # Get the branch name after ->
                            if (
                                ref and ref != "HEAD"
                            ):  # Exclude the simple HEAD reference
                                processed_refs.append(f'"{ref}"')
                        if processed_refs:
                            # Join with comma and space as it's a single tag attribute
                            commit_line += f' tag: {", ".join(processed_refs)}'

                    if message:
                        # Escape double quotes in message
                        message = message.replace('"', '\\"')
                        commit_line += f' msg: "{message}"'

                    mermaid_code += commit_line + "\n"
                    commits_seen[hash_val] = True

            # Note: Handling merge lines (|/ \) is more complex and not fully covered
            # in this simple parser, requires analyzing the graph structure.

        # print(mermaid_code)
        return mermaid_code

    def work(self) -> str:
        """
        执行 Git 命令以获取当前仓库的完整提交历史。

        此方法运行 `git log --all --graph --pretty=format:%h,%d,%s` 命令，
        捕获其标准输出，并打印出来。它还处理命令执行过程中可能出现的错误，
        例如 Git 命令未找到或执行失败。

        Returns:
            str: Git 命令的标准输出，包含格式化的提交历史。

        Raises:
            FileNotFoundError: 如果 'git' 命令未找到。
            subprocess.CalledProcessError: 如果 Git 命令执行失败。
        """
        # 将命令拆分成一个列表，这是更安全的方式
        command = ["git", "log", "--all", "--graph", "--pretty=format:%h,%d,%s"]

        try:
            # 执行命令
            # capture_output=True: 捕获标准输出和标准错误
            # text=True: 将捕获到的输出(bytes)解码为文本(str)
            # check=True: 如果命令返回非零退出码（表示有错误），则会抛出异常
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",  # 明确指定编码，避免乱码问题
            )

            # 捕获的输出存储在 result.stdout 属性中
            git_log_output = result.stdout

            # 现在你可以对这个字符串做任何你想做的事情了
            print("--- 捕获到的 Git Log 输出 ---")
            print(git_log_output)

            # 你甚至可以把它按行分割成一个列表
            log_lines = git_log_output.strip().split("\n")
            print("\n--- 输出的第一行 ---")
            print(log_lines[0])

        except FileNotFoundError:
            print(
                "错误: 'git' 命令未找到。请确保 Git 已经安装并且在系统的 PATH 环境变量中。"
            )
        except subprocess.CalledProcessError as e:
            # 如果 git 命令执行失败 (例如，不在一个 git 仓库中)
            print(f"执行 Git 命令时出错，返回码: {e.returncode}")
            print(f"错误信息 (stderr):\n{e.stderr}")
        return git_log_output

    def run(self) -> str:
        """
        执行完整的 Git 历史获取和 Mermaid 图生成流程。

        此方法首先调用 `work()` 获取 Git 日志输出，然后使用 `generate_mermaid_git_graph()`
        将日志转换为 Mermaid 语法，最后将 Mermaid 代码嵌入到预定义的格式字符串中。

        Returns:
            str: 包含 Mermaid Git Graph 的完整格式化字符串，可以直接在支持 Mermaid 的环境中渲染。
        """
        git_log_output = self.work()
        mermaid_code = self.generate_mermaid_git_graph(git_log_output)
        return self.mermaid_format.format(mermaid_code=mermaid_code)

