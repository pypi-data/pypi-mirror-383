# Example 1: Simple Function Tracing

**Learning Objective**: Understand how to initialize Breadcrumb and trace basic function calls.

```bash
# init project
breadcrumb init example01

# trace run
breadcrumb run -c example01 -t 60 python main.py

# dig deep
breadcrumb query -c example01 --call multiply

# complete flow
breadcrumb query -c example01 --flow
