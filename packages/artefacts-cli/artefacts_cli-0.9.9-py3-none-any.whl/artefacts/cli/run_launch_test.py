from glob import glob
import os
import shutil

import yaml

from .i18n import localise
from .utils import run_and_save_logs
from .result_utils import parse_xml_tests_results, get_TestSuite_error_result
from .parameters import TMP_SCENARIO_PARAMS_YAML
from .result_utils import check_and_prepare_rosbags_for_upload


# custom exceptions raised when trying to run ros2 tests
class Launch_test_CmdNotFoundError(FileNotFoundError):
    pass


class LaunchTestFileNotFoundError(FileNotFoundError):
    pass


class BadLaunchTestFileError(Exception):
    pass


def ros2_run_and_save_logs(
    args, output_path, shell=False, executable=None, env=None, cwd=None
):
    try:
        return_code, stdout, stderr = run_and_save_logs(
            args,
            output_path,
            shell=shell,
            executable=executable,
            env=env,
            cwd=cwd,
            with_output=True,
        )
    except FileNotFoundError:
        raise Launch_test_CmdNotFoundError(
            f"Running {args} failed. Please check that `launch_test` is installed and in the path."
        )
    if return_code == 2:
        # check the proc stderr for `launch_test: error: Test file '[filename]' does not exist`

        if "does not exist" in stderr:
            raise LaunchTestFileNotFoundError(
                f"Running {args} failed. Please check that the launch file exists."
            )
        if "launch_test: error: " in stderr:
            # example errors:
            # "has no attribute 'generate_test_description'"
            # "error: name 'xxx' is not defined"
            raise BadLaunchTestFileError(
                f"Running {args} failed. Check that the launch_test file syntax is correct."
            )

    return return_code


def generate_scenario_parameter_output(params: dict, param_file: str):
    """
    Store `params` in `param_file` and convert to ros2 param file nested format,
    to be used by the launch file
    """
    content = {}
    for k, v in params.items():
        try:
            node, pname = k.split("/")
        except Exception:
            print(
                localise(
                    "Problem with parameter name. Please ensure params are in the format `node/param`"
                )
            )
            return
        if node not in content:
            content[node] = {"ros__parameters": {}}
        # handles nested keys for params in the form of dot notation
        current_level = content[node]["ros__parameters"]
        keys = pname.split(".")
        for key in keys[:-1]:
            if key not in current_level:
                current_level[key] = {}
            current_level = current_level[key]
        current_level[keys[-1]] = v
    with open(param_file, "w") as f:
        yaml.dump(content, f)


def run_ros2_tests(run):
    scenario = run.params
    # TODO: HOW TO ADD  NODE to launch
    # TODO: set params from conf
    # TODO: get params to log
    # TODO: where is the rosbag
    if "params" in run.params:
        # note: fixed filename will lead concurent executions to overwrite each other
        generate_scenario_parameter_output(
            run.params["params"], TMP_SCENARIO_PARAMS_YAML
        )
    # We look for the directory as drilling down will find both
    # the directory as well as the rosbag itself.
    preexisting_rosbags = [
        path for path in glob("**/rosbag2*", recursive=True) if os.path.isdir(path)
    ]
    test_result_file_path = f"{run.output_path}/tests_junit.xml"
    launch_arguments = [
        f"{k}:={v}" for k, v in run.params.get("launch_arguments", {}).items()
    ]

    # Support both ros_testfile and launch_test_file parameters
    test_file = scenario.get("launch_test_file") or scenario.get("ros_testfile")

    command = [
        "launch_test",
        "--junit-xml",
        test_result_file_path,
        test_file,
    ] + launch_arguments

    # save ROS logs in the output dir
    ros_log_dir = os.path.join(run.output_path, "ros_logs")
    user_log_dir = os.path.join(run.output_path, "user")

    # Main: test execution
    # shell=True required to support command list items that are strings with spaces
    # (this way, test_file can be either a path to the launch file or '<package_name> <launch_name>')
    try:
        return_code = ros2_run_and_save_logs(
            " ".join(command),
            shell=True,
            executable="/bin/bash",
            env={
                **os.environ,
                **{
                    "ROS_LOG_DIR": ros_log_dir,
                    "ARTEFACTS_SCENARIO_PARAMS_FILE": TMP_SCENARIO_PARAMS_YAML,
                    "ARTEFACTS_SCENARIO_UPLOAD_DIR": user_log_dir,
                },
            },
            output_path=os.path.join(run.output_path, "test_process_log.txt"),
        )
    except Launch_test_CmdNotFoundError:
        # raise Exception(
        #    f"Running {scenario['ros_testfile']} failed. Please check that the launch file exists."
        # )
        # closes the run properly and mark as errored
        # dict matching junit xml format for test execution error
        result = get_TestSuite_error_result(
            test_file,
            "launch_test command not found",
            "Please check that launch_test is installed and in the path. Exception: {e}",
        )
        results = [result]
        run.log_tests_results(results, False)
        return results, False
    except LaunchTestFileNotFoundError as e:
        result = get_TestSuite_error_result(
            test_file,
            "launch_test file not found",
            f"Please check that the `launch_test_file` or `ros_testfile` config is correct. Exception: {e}",
        )
        results = [result]
        run.log_tests_results(results, False)
        return results, False
    except BadLaunchTestFileError as e:
        result = get_TestSuite_error_result(
            test_file,
            "launch_test file syntax error",
            f"Please check that the file specified in `launch_test_file` or `ros_testfile` config is a valid ros_test file. You may be able to identify issues by doing `launch_test {test_file}`. Exception: {e}",
        )
        results = [result]
        run.log_tests_results(results, False)
        return results, False

    if return_code == 2:
        raise Exception(
            f"Running {test_file} failed. Please check that the launch file exists."
        )

    # zip ROS logs and delete the original folder
    if os.path.exists(ros_log_dir):
        shutil.make_archive(ros_log_dir, "zip", ros_log_dir)
        shutil.rmtree(ros_log_dir)

    # parse xml generated by launch_test
    results, success = parse_xml_tests_results(test_result_file_path)
    # upload logs anyway to help user debug
    run.log_artifacts(run.output_path)
    if success is None:
        # run() in app.py will handle the error message
        return results, success

    # upload any additional files in the folders specified by the user in artefacts.yaml
    for output in scenario.get("output_dirs", []):
        run.log_artifacts(output)

    check_and_prepare_rosbags_for_upload(run, preexisting_rosbags)

    run.log_tests_results(results, success)
    return results, success
