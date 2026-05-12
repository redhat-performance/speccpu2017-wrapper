# SPEC CPU 2017 Benchmark Wrapper

## Description

This wrapper facilitates the automated execution of the SPEC CPU 2017 benchmark suite. SPEC CPU 2017 is an industry-standard benchmark for measuring compute-intensive performance by running a collection of real-world application workloads. The suite measures throughput in SPECrate metrics across integer (intrate) and floating-point (fprate) workloads.

The wrapper provides:
- Automated SPEC CPU 2017 installation from ISO, build, and execution.
- Support for x86_64 (AMD/Intel) and aarch64 (ARM) architectures.
- Automatic GCC version detection and compiler flag adaptation.
- Automatic copy count determination based on available CPUs.
- Disk/filesystem management for benchmark run areas.
- Result collection, CSV/JSON processing, and Pydantic schema validation.
- System configuration metadata capture.
- Integration with test_tools framework.
- Optional Performance Co-Pilot (PCP) integration.

## Command-Line Options

```
SPEC CPU 2017 Options:
  --copies <value>: Number of benchmark copies to run in parallel.
      Defaults to nproc (all available CPUs).
  --test <list>: Comma-separated list of tests to run.
      Valid values: intrate, fprate, or individual benchmarks (e.g., 500.perlbench_r).
      Defaults to "intrate,fprate" (all benchmarks).
  --test_prefix <name>: Prefix applied to test result names.
  --spec_config <file>: SPEC CPU 2017 configuration file to use.
      Defaults to architecture-appropriate Example-gcc-linux config.

Disk/Storage Options:
  --disks <path>: Block device to use for the speccpu run area. If multiple comma-separated
      devices are provided, only the first device is used for formatting and mounting.
  --disk_fs <fs>: Filesystem type to create on --disks device (default: xfs).
  --no_disk: Automatically select the filesystem with the most free space.
  --installed: Indicate that the kit is already installed. Skips disk formatting/mounting
      and suppresses ISO unmount on exit. The ISO is still mounted and install.sh is still
      run to ensure the kit is up to date at the --speccpu_run_dir location.
  --speccpu_iso_file <path>: Path to the SPEC CPU 2017 ISO file.
  --speccpu_iso_mnt <path>: Mount point for the ISO (default: /speccpu).
  --speccpu_run <path>: Mount point for benchmark execution area (default: /speccpu_run).
  --speccpu_run_dir <dir>: Directory of a pre-installed SPEC CPU 2017 kit.
  --uploads <path>: Directory containing the ISO file.

General test_tools Options:
  --debug: Enables bash -x output, useful for debugging issues with wrappers.
  --home_parent <value>: Parent home directory. Defaults to current working directory.
  --host_config <value>: Host configuration name, defaults to current hostname.
  --iterations <value>: Number of times to run the test, defaults to 1.
  --iteration_default <value>: Value to set iterations to, if default is not set.
  --no_system_packages: Do not install system packages via the system package manager.
  --no_pip_packages: Do not install python pip packages via pip.
  --no_pkg_install: Test is not to install any packages.
  --run_user <user>: User that is actually running the test. Defaults to current user.
  --sys_type <type>: Type of system (aws, azure, hostname). Defaults to hostname.
  --test_tools_release <tag>: Version tag of test tools to use.
  --sysname <name>: Name of the system running. Defaults to hostname.
  --json_skip: Skip JSON conversion of test CSV results, default is 0.
  --verify_skip: Skip test verifications against output, default is 0.
  --tuned_setting <name>: Used in naming the results directory. For RHEL, defaults to
      current active tuned profile. For non-RHEL systems, defaults to 'none'.
  --use_pcp: Enable Performance Co-Pilot monitoring during test execution.
  --tools_git <value>: Git repo to retrieve the required tools from.
      Default: https://github.com/redhat-performance/test_tools-wrappers
  --usage: Display this usage message.
```

## What the Script Does

The `run_speccpu` script performs the following workflow:

1. **Tool Acquisition**:
   - Downloads the test_tools-wrappers repository if not present (default: ~/test_tools).
   - Attempts download via wget, then curl, then git clone as fallback.
   - Sources error codes and general setup utilities.

2. **Package Installation**:
   - Installs required dependencies via package_tool using speccpu2017.json.
   - Dependencies are defined for different OS variants (RHEL, Ubuntu, SLES, Amazon Linux).

3. **Disk and Filesystem Setup**:
   - If `--disks` is provided, wipes the device, creates a new filesystem, and mounts it.
   - If `--no_disk` is used, automatically selects the filesystem with the most free space.
   - If `--installed` is used with `--speccpu_run_dir`, skips disk formatting/mounting (uses the provided directory directly). Note: the ISO is still mounted and install.sh is still executed.
   - Interactive disk selection via grab_disks utility if no disk option is specified.

4. **SPEC CPU 2017 Installation**:
   - Mounts the ISO image to /speccpu (or configured mount point).
   - Runs the SPEC install.sh script with automated responses.
   - Validates that the installed version is >= 1.1.8.

5. **Configuration Generation**:
   - Detects CPU architecture via /proc/cpuinfo.
   - Selects the appropriate configuration file:
     - x86_64 (Intel/AMD): `Example-gcc-linux-x86.cfg`
     - aarch64 (ARM): `Example-gcc-linux-aarch64.cfg`
   - Applies GCC version-specific modifications:
     - Removes hardcoded devtoolset GCC paths.
     - Disables peak tuning (base-only benchmarking).
     - Removes CPU-model-specific ABI flags for portability.
     - Detects GCC version and enables/disables appropriate compiler flags.

6. **Build Phase**:
   - Sources the SPEC CPU 2017 shell environment (shrc).
   - Determines copy count (defaults to nproc).
   - Clobbers any previous builds.
   - Builds each selected test individually using `runcpu --action=build`.

7. **Test Execution**:
   - Optionally initializes PCP monitoring with benchmark-specific metrics.
   - For each test:
     - Records start timestamp.
     - Executes: `runcpu --config=<cfg> --copies=<N> <test>`.
     - Processes results via generate_results_csv().
     - Records end timestamp.
     - Stops PCP monitoring (if enabled).

8. **Result Processing**:
   - Extracts benchmark results from raw SPEC CPU 2017 output files.
   - Parses per-benchmark metrics: name, base copies, base run time, and base rate.
   - Generates CSV files with standardized headers.
   - Converts CSV to JSON via csv_to_json.
   - Publishes metrics to PCP (if enabled) via results2pcp_add_value.

9. **Validation**:
   - Validates results against the Pydantic schema (results_schema.py).
   - Ensures all required fields are present, numeric fields are positive, and Base_Rate is finite.
   - Uses verify_results from test_tools.

10. **Output**:
    - Creates results directory: `results_speccpu_<tuned_setting>_<timestamp>`.
    - Copies all SPEC CPU 2017 result files.
    - Archives results into a tarball: `results_speccpu2017_<tuned_setting>.tar`.
    - Saves results to configured storage via save_results.

## Dependencies

**SPEC CPU 2017 ISO**: The benchmark suite itself must be obtained separately from [SPEC](https://www.spec.org/cpu2017/). The wrapper expects an ISO file provided via `--speccpu_iso_file` or located in the `--uploads` directory.

**RHEL / Amazon Linux packages**: bc, libnsl, gcc-gfortran, nvme-cli, perf, git, unzip, zip, libxcrypt-compat

**SLES packages**: gcc, make, gcc-fortran, gcc-c++, bc, git, unzip, zip

**Ubuntu packages**: bc, zip, unzip, git, gfortran, g++, gcc

To run:
```bash
git clone https://github.com/redhat-performance/speccpu2017-wrapper
cd speccpu2017-wrapper/speccpu2017
sudo sudo ./run_speccpu --speccpu_iso_file /path/to/cpu2017.iso
```

**Note**: Root or sudo privileges are required for ISO mounting (`mount`), disk formatting (`wipefs`, `mkfs`), and filesystem mounting operations.

The script will automatically detect your CPU architecture and select appropriate defaults.

## The SPEC CPU 2017 Benchmark

SPEC CPU 2017 is a benchmark suite from the Standard Performance Evaluation Corporation that measures compute-intensive performance using workloads derived from real-world applications. The wrapper targets the **SPECrate** metric, which measures throughput by running multiple parallel copies of each workload.

### Benchmark Suites

SPEC CPU 2017 includes two rate (throughput) suites:

#### Integer Rate (intrate) — 10 Benchmarks

| Benchmark | Application Domain |
|-----------|--------------------|
| 500.perlbench_r | Perl interpreter |
| 502.gcc_r | GNU C Compiler |
| 505.mcf_r | Route planning (combinatorial optimization) |
| 520.omnetpp_r | Discrete event simulation |
| 523.xalancbmk_r | XML to HTML transformation |
| 525.x264_r | Video compression |
| 531.deepsjeng_r | Chess engine (alpha-beta search) |
| 541.leela_r | Go game engine (Monte Carlo tree search) |
| 548.exchange2_r | Sudoku solver |
| 557.xz_r | General data compression |

#### Floating-Point Rate (fprate) — 13 Benchmarks

| Benchmark | Application Domain |
|-----------|--------------------|
| 503.bwaves_r | Computational fluid dynamics |
| 507.cactuBSSN_r | General relativity (spacetime simulation) |
| 508.namd_r | Molecular dynamics |
| 510.parest_r | Finite element PDE solver |
| 511.povray_r | Ray tracing |
| 519.lbm_r | Lattice Boltzmann fluid dynamics |
| 521.wrf_r | Weather forecasting |
| 526.blender_r | 3D rendering |
| 527.cam4_r | Climate modeling |
| 538.imagick_r | Image manipulation |
| 544.nab_r | Molecular dynamics (nucleic acids) |
| 549.fotonik3d_r | Computational electromagnetics |
| 554.roms_r | Ocean modeling |

### Key Concepts

1. **Copies**: The number of parallel instances of each benchmark. Higher copy counts measure throughput scaling. This wrapper defaults to `nproc` (all available CPUs), meaning one copy per logical CPU.

2. **Base vs. Peak**: SPEC CPU 2017 supports two tuning levels. This wrapper runs **base only**, which uses conservative, portable compiler flags. Peak tuning is explicitly disabled.

3. **SPECrate Metric**: The performance score for throughput benchmarks. Higher values indicate better performance. Each benchmark produces its own rate score based on copies and runtime.

4. **Configuration File**: A `.cfg` file that defines compiler paths, optimization flags, and build settings for each benchmark. The wrapper uses SPEC-provided example GCC configurations, modified for the detected system.

## Output Files

The results directory (`results_speccpu_<tuned_setting>_<timestamp>/`) contains:

- **result/**: Complete SPEC CPU 2017 result directory containing:
  - `.txt` result summary files with per-benchmark scores.
  - `.log` files with detailed build and run output.
  - `.csv` and `.html` formatted result reports.
- **\<spec_result_name\>.results.csv**: Processed CSV files with per-benchmark metrics (Benchmarks, Base_copies, Base_Run_Time, Base_Rate). Filenames are derived from the SPEC result `.txt` files.
- **speccpu_res.json**: JSON results validated against the Pydantic schema.
- **meta_data*.yml**: System metadata (CPU info, memory, kernel version).
- **PCP data** (if `--use_pcp` option used): Performance Co-Pilot monitoring data with per-benchmark metric values.

The final archive is saved as: `results_speccpu2017_<tuned_setting>.tar`

## Examples

### Basic run with defaults
```bash
sudo ./run_speccpu --speccpu_iso_file /path/to/cpu2017.iso
```
This runs with:
- All benchmarks (intrate and fprate)
- Copies = number of available CPUs
- Automatic architecture detection and config selection
- 1 iteration
- Interactive disk selection

### Run only integer rate benchmarks
```bash
sudo ./run_speccpu --speccpu_iso_file /path/to/cpu2017.iso --test intrate
```
Runs only the 10 integer rate benchmarks.

### Run specific benchmarks
```bash
sudo ./run_speccpu --speccpu_iso_file /path/to/cpu2017.iso --test "500.perlbench_r,502.gcc_r,505.mcf_r"
```
Runs only the specified individual benchmarks.

### Run with a specific disk device
```bash
sudo ./run_speccpu --speccpu_iso_file /path/to/cpu2017.iso --disks /dev/nvme1n1 --disk_fs xfs
```
Creates an XFS filesystem on /dev/nvme1n1, mounts it, and uses it as the benchmark run area.

### Run without dedicated disk (use existing filesystem)
```bash
sudo ./run_speccpu --speccpu_iso_file /path/to/cpu2017.iso --no_disk
```
Automatically selects the filesystem with the most free space.

### Run with pre-installed kit directory
```bash
sudo ./run_speccpu --installed --speccpu_run_dir /opt/speccpu2017 --speccpu_iso_file /path/to/cpu2017.iso
```
Skips disk formatting/mounting and uses the specified directory. The ISO is still required for install verification.

### Run with reduced copies
```bash
sudo ./run_speccpu --speccpu_iso_file /path/to/cpu2017.iso --copies 16
```
Runs 16 parallel copies per benchmark instead of using all CPUs.

### Run multiple iterations
```bash
sudo ./run_speccpu --speccpu_iso_file /path/to/cpu2017.iso --iterations 3
```
Runs the full benchmark suite 3 times for consistency verification.

### Run with PCP monitoring
```bash
sudo ./run_speccpu --speccpu_iso_file /path/to/cpu2017.iso --use_pcp
```
Collects Performance Co-Pilot data during the run, with per-benchmark metric tracking.

### Combination example
```bash
sudo ./run_speccpu --speccpu_iso_file /path/to/cpu2017.iso --test fprate --copies 32 \
    --iterations 3 --disks /dev/nvme1n1 --use_pcp --tuned_setting throughput-performance
```
Runs floating-point rate benchmarks with 32 copies, 3 iterations, on a dedicated NVMe device, with PCP monitoring and a specific tuned profile label.

## How Copy Count and Configuration Works

### Copy Count (Parallelism)

The wrapper determines the number of parallel benchmark copies:

1. If `--copies` is specified, that value is used directly.
2. Otherwise, defaults to `nproc` — one copy per available logical CPU.
3. Each benchmark runs all copies simultaneously, measuring throughput.

For rate (throughput) benchmarking, maximizing copies typically yields the highest SPECrate scores, as it exercises all available CPU resources.

### Architecture Detection

The wrapper inspects `/proc/cpuinfo` model name to determine the CPU vendor:

- **Intel or AMD detected**: Intended to use `Example-gcc-linux-x86.cfg`.
- **Other (including ARM/aarch64)**: Uses `Example-gcc-linux-aarch64.cfg`.

**Note**: The current script has a known issue where the glob pattern matching for Intel/AMD uses quoted wildcards, which may cause x86 systems to fall through to the aarch64 config. Use `--spec_config` to explicitly specify the correct config file if needed.

### GCC Version Adaptation

The wrapper detects the installed GCC version and applies necessary modifications:

| GCC Version | Adaptation |
|-------------|------------|
| < 10 | Disables `preENV_LD_LIBRARY_PATH` references |
| >= 10 | Enables `GCCge10` flag block for updated compiler flags |
| >= 14 | Adds `-Wno-error=implicit-int` for 527.cam4_r |
| >= 14 | Adds `-Wno-incompatible-pointer-types` for 500.perlbench_r |

### Configuration Modifications

The wrapper applies several modifications to the SPEC-provided example config:

1. **Removes devtoolset GCC path**: Eliminates hardcoded `/opt/rh/devtoolset-*/root/usr/bin/gcc` references, using the system GCC instead.
2. **Disables peak tuning**: Sets base-only mode for consistent, portable results.
3. **Removes ABI flags**: Strips `-mabi=lp64` flags for broader compatibility.

## Disk and Storage Management

The wrapper supports several strategies for managing the benchmark run area, which needs sufficient space for the full SPEC CPU 2017 installation and build artifacts (~20+ GiB).

### Storage Options

| Option | Behavior |
|--------|----------|
| `--disks <device>` | Wipes first device, creates filesystem, mounts to --speccpu_run |
| `--no_disk` | Selects existing filesystem with most free space |
| `--speccpu_run_dir <dir>` | Uses the specified directory, skips disk formatting/mounting |
| *(none)* | Interactive disk selection via grab_disks utility |

The `--disks`, `--speccpu_run_dir`, and `--no_disk` options participate in mutual exclusion — the wrapper validates that only one is specified and exits with `E_USAGE` if conflicting options are provided. Note that `--installed` does not participate in this validation and can be combined with other options.

### Filesystem Setup Steps

When `--disks` is provided:
1. Validates the block device exists.
2. Wipes existing filesystem signatures (`wipefs -a`).
3. Creates a new filesystem (`mkfs.<disk_fs>`).
4. Mounts to the specified run path (default: /speccpu_run).
5. Clears and recreates the run directory.

## SPEC CPU 2017 Installation

### ISO-Based Installation

1. The ISO file is mounted to the configured mount point (default: /speccpu).
2. The SPEC `install.sh` script is run with automated input responses.
3. The installed version is verified to be >= 1.1.8.
4. If the version check fails, the wrapper exits with an error.

### Pre-Installed Kit

When `--installed` and `--speccpu_run_dir` are specified, the wrapper skips disk formatting/mounting and uses the provided directory. Note that the ISO is still mounted and `install.sh` is still executed into the target directory. On exit, the wrapper skips ISO/disk unmounting and instead cleans up the `recorded` marker file. An ISO file is still required even with `--installed`.

## PCP Metrics

When `--use_pcp` is enabled, the wrapper tracks the following Performance Co-Pilot metrics:

- **Generic metrics**: iteration, running, numthreads, runtime, throughput, latency
- **Per-benchmark metrics**: One metric per benchmark (e.g., `500.perlbench_r`, `502.gcc_r`, etc.) — 21 metrics total for all intrate and fprate benchmarks.

Metrics are initialized to NaN before execution and updated with actual Base_Rate values as results become available.

## Return Codes

The script uses standardized error codes from the test_tools error_codes module:

- **0**: Success
- **E_PACKAGE_TOOL_PACKAGING**: Dependency installation failure
- **E_USAGE**: Invalid arguments or conflicting options (e.g., multiple run location strategies)
- **E_GENERAL**: General execution errors including:
  - Block device validation failures
  - Filesystem creation or mount failures
  - ISO mount failures
  - SPEC CPU 2017 install script failures
  - Version check failures (< 1.1.8)
  - CSV-to-JSON conversion failures
  - Schema validation failures

The exit code from verify_results (schema validation) is propagated as the final return code when result processing fails.

## Notes

### Architecture Support
- **x86_64**: Full support for AMD and Intel CPUs using SPEC-provided GCC configuration.
- **aarch64**: Full support for ARM CPUs using the SPEC-provided ARM GCC configuration.

### SPEC CPU 2017 Licensing
- SPEC CPU 2017 is a commercial benchmark. The ISO must be obtained separately from [spec.org](https://www.spec.org/cpu2017/).
- The wrapper automates installation and execution but does not distribute the benchmark itself.

### GCC Compatibility
- The wrapper is designed to work with system-provided GCC.
- GCC versions 8 through 14+ are supported with automatic flag adaptation.
- GCC 14 introduced stricter type-checking defaults that break certain benchmarks (cam4, perlbench); the wrapper applies targeted workarounds.

### Disk Space Requirements
- A full SPEC CPU 2017 installation requires approximately 10-15 GiB.
- Build artifacts for all benchmarks add approximately 5-10 GiB.
- Running all benchmarks with high copy counts may require additional temporary space.
- Use a dedicated disk (`--disks`) or ensure sufficient free space on the target filesystem.

### Base-Only Benchmarking
- The wrapper disables peak tuning and runs base-only configurations.
- Base results use conservative, portable compiler flags.
- This provides consistent, comparable results across different systems.
- For official SPEC CPU 2017 submissions, refer to SPEC's run and reporting rules.

### Copy Count Considerations
- Default (`nproc`) uses all logical CPUs, maximizing throughput.
- Reduce copies for memory-constrained systems, as each copy requires its own working set.
- Some benchmarks (e.g., 503.bwaves_r, 549.fotonik3d_r) have large memory footprints and may require fewer copies on systems with limited RAM.

### Performance Tips
- Run multiple iterations to verify consistency.
- Ensure the system is idle (no competing workloads) for best results.
- Use a dedicated NVMe or SSD device for the run area to minimize I/O bottlenecks during build and execution.
- Set the CPU frequency governor to "performance" for reproducible results.
- On RHEL systems, use the `throughput-performance` tuned profile.
- Use `--use_pcp` to collect detailed system-level performance counters alongside benchmark scores.

### Special Cases

- **RHEL with FlexiBLAS**: On RHEL 9+, the system compiler and math libraries use FlexiBLAS. The wrapper's SPEC config uses system GCC directly, so FlexiBLAS does not affect SPEC CPU 2017 builds.
- **Amazon Linux**: Package names may differ slightly; the speccpu2017.json config handles Amazon Linux as a RHEL-like variant.
- **SLES**: Requires gcc-fortran and gcc-c++ packages rather than RHEL-style gcc-gfortran; handled by speccpu2017.json.
- **devtoolset**: The wrapper explicitly removes devtoolset GCC path references from the config file, ensuring the system-default GCC is used regardless of whether devtoolset is installed.

### Troubleshooting

- **ISO mount failure**: Ensure the ISO file exists at the specified path and that the mount point is available. Verify that the user has root/sudo privileges for mount operations.
- **Version check failure**: The wrapper requires SPEC CPU 2017 version >= 1.1.8. Obtain an updated ISO from SPEC if your version is older.
- **Build failures**: Check that all compiler packages (gcc, gcc-gfortran/gfortran, gcc-c++/g++) are installed. Review build logs in the result directory.
- **GCC 14 build errors**: The wrapper applies known workarounds automatically. If new errors appear with newer GCC versions, check for implicit-int or pointer-type warnings being promoted to errors.
- **Low copy count performance**: If SPECrate scores are unexpectedly low, verify that copies match the number of available CPUs and that no CPU resources are being consumed by other processes.
- **Disk space errors**: SPEC CPU 2017 requires significant disk space. Use `df -h` to verify available space before running, especially when using `--no_disk`.
