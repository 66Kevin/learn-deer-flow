DeerFlow是什么？

字节跳动开源的SuperAgent Harness，专注于深度研究和多Agent编排

核心架构：Plan -> Act -> Reflect

三角循环：

- Planner：负责任务拆解，把复杂问题拆解成步骤
- Actor：负责执行工具调用，如搜索，代码，文件
- Reflector：负责质量审核，检查结果是否符合预期

这个架构和LangChain的ReAct类似，但DeerFlow在Harness层面做了更深的工程化

DeerFlow的Harness设计

- 约束（Constraints）

  - Planner输出每个步骤时，系统检查工具规范、危险操作、超时：

    ```python
    当前步骤是否在允许的Tool范围内？
    是否有危险操作？
    是否超时？
    ```
- 告知（Informing）

  - Reflector的审核结果反馈给Planner，形成上下文积累：

    ```python
    第N步失败 -> Reflector指出原因 -> Planner在N+1步注入纠正策略
    ```
- 验证（Verification）

  - 每个Actor输出都经过Reflector的检查：数据完整性，引用有效性，结论依据
- 纠错（Correction）

  - DeerFlow不是简单重试，而是让Planner重新生成“绕过已知失败点的策略”

DeerFlow的MultiAgent设计

WIP……
