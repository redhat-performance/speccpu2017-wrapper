Automation wrapper for speccpu2017

Description:
           This wrapper runs the speccpu2017 benchmark.
           The SPEC CPU® 2017 benchmark package contains SPEC's next-generation,
           industry-standardized, CPU intensive suites for measuring and comparing
           compute intensive performance, stressing a system's processor, memory
           subsystem and compiler.
  
Location of underlying workload: https://www.spec.org/cpu2017/  Requires a license to run.

Packages required: bc,libnsl,gcc-gfortran

To run:
```
[root@hawkeye ~]# git clone https://github.com/redhat-performance/speccpu2017-wrapper
[root@hawkeye ~]# specpu2017-wrapper/speccpu2017/run_speccpu
```


```
Options
  --copies: number of copies of speccpu2017 to run.  Default is nprocs
  --spec_config: Spec configuration file to use, default is /speccpu_run/config/Example-gcc-linux-aarch64.cfg
    or /speccpu_run/config/Example-gcc-linux-x86.cfg
  --test: comma separated list of speccpu2017 tests running.
  --test_prefix: prefix name of the test results
General options
  --home_parent <value>: Our parent home directory.  If not set, defaults to current working directory.
  --host_config <value>: default is the current host name.
  --iterations <value>: Number of times to run the test, defaults to 1.
  --pbench: use pbench-user-benchmark and place information into pbench, defaults to do not use.
  --pbench_user <value>: user who started everything. Defaults to the current user.
  --pbench_copy: Copy the pbench data, not move it.
  --pbench_stats: What stats to gather. Defaults to all stats.
  --run_label: the label to associate with the pbench run. No default setting.
  --run_user: user that is actually running the test on the test system. Defaults to user running wrapper.
  --sys_type: Type of system working with, aws, azure, hostname.  Defaults to hostname.
  --sysname: name of the system running, used in determining config files.  Defaults to hostname.
  --tuned_setting: used in naming the tar file, default for RHEL is the current active tuned.  For non
    RHEL systems, default is none.
  --usage: this usage message.
```

Note: The script does not install pbench for you.  You need to do that manually.
