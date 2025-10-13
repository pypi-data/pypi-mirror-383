executor_template_1: str = \
    """from je_api_testka import execute_action, read_action_json

execute_action(
    read_action_json(
        r"{temp}"
    )
)
"""

executor_template_2: str = \
    """from je_api_testka import execute_files, get_dir_files_as_list

execute_files(
    get_dir_files_as_list(
        r"{temp}"
    )
)
"""

bad_executor_template_1: str = \
    """
# This example is primarily intended to remind users of the importance of verifying input.
from je_api_testka import execute_action, read_action_json
    
execute_action(
    read_action_json(
        r"{temp}"
    )
)
"""
