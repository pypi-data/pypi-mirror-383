LESSONS = {
    "ls": {
        "brief": "Prints contents of a directory",
        "usage": "ls",
        "options": {
            "-l": "Use a long listing format",
            "-a": "Include hidden files",
            "-h": "Human readable file sizes",
        },
        "ethical": (
            "Helps enumerate files and hidden contents on target systems; "
            "crucial for reconnaissance and understanding directory structure."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/ls_lab",
        "setup": ["file1.txt", "file2.txt", ".hiddenfile"],
        "practice": (
            "List all files, including hidden ones, using 'ls -la'. "
            "Try different options like '-h' to see human readable sizes."
        )
    },
    "pwd": {
        "brief": "Print current directory path",
        "usage": "pwd",
        "options": {
            "--help": "Display help info",
            "-P": "Print physical directory without symbolic links",
            "-L": "Print logical directory with symbolic links",
        },
        "ethical": (
            "Important for knowing attackers current location when navigating systems."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/pwd_lab",
        "setup": [],
        "practice": (
            "Type 'pwd' to display the present working directory. "
            "Try with '-P' and '-L' options to see differences."
        )
    },
    "mkdir": {
        "brief": "Create directories",
        "usage": "mkdir [directory]",
        "options": {
            "-p": "Create parent directories as needed",
            "-v": "Verbose output when creating directories",
            "-m": "Set permissions (mode) when creating a directory",
        },
        "ethical": (
            "Helps to organize files or prepare directories during engagements."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/mkdir_lab",
        "setup": [],
        "practice": (
            "In the lab directory, create a new folder named 'testdir' with 'mkdir testdir'. "
            "Try creating nested folders using 'mkdir -p parent/child'. "
            "Use '-v' to see detailed output."
        )
    },
    "cd": {
        "brief": "Change the current directory",
        "usage": "cd [directory]",
        "options": {
            "..": "Move up one directory",
            "-": "Switch to previous directory",
            "~": "Change to home directory",
        },
        "ethical": (
            "Essential to move through directory trees and access files during penetration testing."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/cd_lab",
        "setup": ["dir/"],
        "practice": (
            "Change into the 'dir' directory using 'cd dir'. "
            "Then move up one level using 'cd ..'. "
            "Try switching between directories using 'cd -' and going home with 'cd ~'."
        )
    },
    "touch": {
        "brief": "Create or update file timestamps",
        "usage": "touch [file]",
        "options": {
            "-c": "Do not create file if it does not exist",
            "-a": "Change only access time",
            "-m": "Change only modification time",
        },
        "ethical": (
            "Useful to create empty files or timestamp files during exploits, stealthy operations."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/touch_lab",
        "setup": [],
        "practice": (
            "Create a new empty file 'newfile.txt' using 'touch newfile.txt'. "
            "Update only access or modification times with '-a' or '-m' options."
        )
    },
    "echo": {
        "brief": "Display a line of text",
        "usage": "echo [text]",
        "options": {
            "-n": "Do not print the trailing newline",
            "-e": "Enable interpretation of backslash escapes",
            "--help": "Show help information",
        },
        "ethical": (
            "Often used in scripts for output or crafting payloads during scripting in engagements."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/echo_lab",
        "setup": [],
        "practice": (
            "Print text to the terminal: e.g. 'echo Hello World'. "
            "Use 'echo -n' to avoid newlines, or 'echo -e' to interpret escape sequences."
        )
    },
    "cat": {
        "brief": "Concatenate and show file contents",
        "usage": "cat [file]",
        "options": {
            "-n": "Number all output lines",
            "-v": "Show non-printing characters",
            "-A": "Show all characters including non-printing",
        },
        "ethical": (
            "Critical for reading logs and configuration files during penetration testing."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/cat_lab",
        "setup": ["file1.txt", "file2.txt"],
        "practice": (
            "Show contents of files using 'cat file1.txt'. "
            "Try numbering lines with 'cat -n file1.txt'."
        )
    },
    "less": {
        "brief": "View file content interactively",
        "usage": "less [file]",
        "options": {
            "-N": "Show line numbers",
            "+F": "Scroll forward and monitor file",
            "--help": "Show help",
        },
        "ethical": (
            "Facilitates reading large files or logs when auditing systems."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/less_lab",
        "setup": ["file1.txt"],
        "practice": (
            "Open files with 'less file1.txt'. "
            "Try showing line numbers with '-N' and follow file updates with '+F'."
        )
    },
    "head": {
        "brief": "Show the first part of files",
        "usage": "head [file]",
        "options": {
            "-n": "Number of lines to show",
            "-c": "Number of bytes to show",
            "-v": "Always show headers",
        },
        "ethical": (
            "Useful to quickly inspect file beginnings, config snippets, or scripts."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/head_lab",
        "setup": ["file1.txt"],
        "practice": (
            "Display the first 10 lines of a file with 'head file1.txt'. "
            "Change number of lines with '-n', and bytes with '-c'."
        )
    },
    "tail": {
        "brief": "Show the last part of files",
        "usage": "tail [file]",
        "options": {
            "-n": "Number of lines to show",
            "-f": "Follow file content as it grows",
            "-c": "Number of bytes to show",
        },
        "ethical": (
            "Monitor logs and real-time system activity during penetration tests."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/tail_lab",
        "setup": ["file1.txt"],
        "practice": (
            "Show the last 10 lines with 'tail file1.txt'. "
            "Follow file changes live using 'tail -f'."
        )
    },
    "cp": {
        "brief": "Copy files and directories",
        "usage": "cp [options] source destination",
        "options": {
            "-r": "Copy directories recursively",
            "-a": "Archive mode; copy directories preserving attributes",
            "-v": "Verbose output showing copied files"
        },
        "ethical": (
            "Copying files allows duplication or backup of sensitive data during engagements."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/cp_lab",
        "setup": ["file1.txt", "dir1/"],
        "practice": (
            "Copy 'file1.txt' to 'file1_copy.txt'. "
            "Copy directory 'dir1' recursively to 'dir1_backup' using 'cp -r'. "
            "Try using '-v' to see verbose output and '-a' to preserve attributes."
        )
    },
    "mv": {
        "brief": "Move or rename files and directories",
        "usage": "mv [options] source destination",
        "options": {
            "-v": "Verbose mode, show files being moved",
            "-i": "Prompt before overwrite",
            "-n": "Do not overwrite existing files"
        },
        "ethical": (
            "Moving or renaming files is useful for organizing or hiding evidence on a system."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/mv_lab",
        "setup": ["file1.txt", "file2.txt"],
        "practice": (
            "Rename 'file1.txt' to 'file1_renamed.txt'. "
            "Move 'file2.txt' into a new folder 'moved_files' after creating it. "
            "Use '-i' to prompt on overwrite and '-v' to view operations."
        )
    },
    "rm": {
        "brief": "Remove files or directories",
        "usage": "rm [options] file...",
        "options": {
            "-r": "Remove directories and their contents recursively",
            "-f": "Force removal without prompt",
            "-i": "Prompt before each removal"
        },
        "ethical": (
            "File and directory removal is critical to cover tracks and delete unwanted files."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/rm_lab",
        "setup": ["file1.txt", "dir1/", "dir1/file2.txt"],
        "practice": (
            "Remove 'file1.txt' safely with '-i' prompt. "
            "Remove directory 'dir1' and contents recursively using 'rm -r'. "
            "Use '-f' to force delete without prompts."
        )
    },
    "rmdir": {
        "brief": "Remove empty directories",
        "usage": "rmdir [options] directory...",
        "options": {
            "--ignore-fail-on-non-empty": "Do not complain if directory is non-empty",
            "-p": "Remove parent directories if they become empty",
            "--help": "Display help and exit"
        },
        "ethical": (
            "Used to clean up empty directories, keeping file system tidy during audits."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/rmdir_lab",
        "setup": ["emptydir/", "parentdir/childdir/"],
        "practice": (
            "Remove an empty directory 'emptydir' using 'rmdir'. "
            "Remove nested directories 'parentdir/childdir' using '-p' option. "
            "Use '--ignore-fail-on-non-empty' to suppress errors on non-empty dirs."
        )
    },
    "file": {
        "brief": "Determine file type",
        "usage": "file [options] file...",
        "options": {
            "-b": "Brief output, no filename",
            "-i": "Output MIME type string",
            "--mime": "Output MIME type"
        },
        "ethical": (
            "Helps identify file formats which attackers or admins use for reconnaissance."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/file_lab",
        "setup": ["file1.txt", "image.png"],
        "practice": (
            "Check type of 'file1.txt' and 'image.png' using 'file'. "
            "Try '-b' for brief output and '-i' or '--mime' for MIME type info."
        )
    },
    "stat": {
        "brief": "Display detailed file status",
        "usage": "stat [options] file...",
        "options": {
            "-c": "Format output according to string",
            "-t": "Print info in terse form",
            "--format": "Specify output format"
        },
        "ethical": (
            "Used to gather file metadata such as permissions, timestamps, and ownership."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/stat_lab",
        "setup": ["file1.txt"],
        "practice": (
            "View detailed info on 'file1.txt' using 'stat file1.txt'. "
            "Try concise output with '-t' and custom formatting with '-c' or '--format'."
        )
    },
    "chmod": {
        "brief": "Change file permissions",
        "usage": "chmod [options] mode file...",
        "options": {
            "-R": "Recursively change permissions",
            "u+x": "Add execute permission for owner",
            "--help": "Display help text"
        },
        "ethical": (
            "Modifying permissions controls access, crucial for system security management."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/chmod_lab",
        "setup": ["script.sh"],
        "practice": (
            "Add execute permission to 'script.sh' using 'chmod u+x script.sh'. "
            "Change permissions recursively in folders with '-R'. "
            "Use '--help' to see command options."
        )
    },
    "chown": {
        "brief": "Change file ownership",
        "usage": "chown [options] owner[:group] file...",
        "options": {
            "-R": "Recursively change ownership",
            "--from": "Change only files owned by specified user",
            "--help": "Show help info"
        },
        "ethical": (
            "Ownership changes may help attackers escalate privileges or maintain persistence."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/chown_lab",
        "setup": ["file1.txt"],
        "practice": (
            "Change ownership of 'file1.txt' to a different user with 'chown user file1.txt'. "
            "Use '-R' to apply recursively and '--from' to restrict changes."
        )
    },
    "sudo": {
        "brief": "Execute commands with elevated privileges",
        "usage": "sudo [options] command",
        "options": {
            "-u": "Run command as a different user",
            "-k": "Invalidate user's cached credentials",
            "--validate": "Update user's cached credentials"
        },
        "ethical": (
            "Allows authorized users to perform administrative tasks securely."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/sudo_lab",
        "setup": [],
        "practice": (
            "Run 'sudo ls /root' to list root-owned files (if permitted). "
            "Try running commands as different users with '-u'. "
            "Invalidate or validate cached credentials with '-k' and '--validate'."
        )
    },
    "whoami": {
        "brief": "Display current user identity",
        "usage": "whoami [options]",
        "options": {
            "--help": "Show help message",
            "--version": "Show version info"
        },
        "ethical": (
            "Useful for checking effective user identity during escalation or automation."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/whoami_lab",
        "setup": [],
        "practice": (
            "Run 'whoami' to show your current username. "
            "Use '--help' to view usage info and '--version' for version details."
        )
    },
    "id": {
        "brief": "Display user and group IDs",
        "usage": "id [options] [username]",
        "options": {
            "-u": "Display effective user ID",
            "-g": "Display effective group ID",
            "-n": "Display names instead of numeric IDs"
        },
        "ethical": (
            "Helps verify user identity and group membership during security audits and penetration tests."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/id_lab",
        "setup": [],
        "practice": (
            "Run 'id' to show your user and group IDs. "
            "Use '-u' to view your effective user ID, '-g' for group ID, and '-n' to show names instead of numbers."
        )
    },
    "ps": {
        "brief": "View running processes",
        "usage": "ps [options]",
        "options": {
            "aux": "Show all running processes with detailed info",
            "-ef": "Alternative full-format listing of all processes",
            "-o": "Customize output format"
        },
        "ethical": (
            "Process listing helps monitor active applications and detect suspicious activities."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/ps_lab",
        "setup": [],
        "practice": (
            "Use 'ps aux' to list all running processes. "
            "Try 'ps -ef' for another detailed view. "
            "Use 'ps -o pid,comm,user' to customize output columns."
        )
    },
    "top": {
        "brief": "Display dynamic real-time process view",
        "usage": "top [options]",
        "options": {
            "-o": "Sort by a specific column",
            "-p": "Monitor specific PIDs",
            "-n": "Number of iterations before exit"
        },
        "ethical": (
            "Allows real-time resource monitoring to understand system load and running tasks."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/top_lab",
        "setup": [],
        "practice": (
            "Run 'top' to view processes dynamically. "
            "Use '-o %CPU' to sort by CPU usage. "
            "Monitor specific process IDs with '-p' and limit updates with '-n'."
        )
    },
    "htop": {
        "brief": "Enhanced interactive process viewer",
        "usage": "htop [options]",
        "options": {
            "F4": "Search for processes",
            "F9": "Kill a selected process",
            "--help": "Show help information"
        },
        "ethical": (
            "Improved interface for process management during system auditing."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/htop_lab",
        "setup": [],
        "practice": (
            "Open 'htop' to view processes interactively. "
            "Use F4 to search for processes by name. "
            "Use F9 to kill a process. "
            "Use '--help' to see command options."
        )
    },
    "kill": {
        "brief": "Send signals to processes",
        "usage": "kill [options] pid",
        "options": {
            "-9": "Force kill signal (SIGKILL)",
            "-15": "Graceful termination (SIGTERM)",
            "-l": "List available signals"
        },
        "ethical": (
            "Vital for terminating rogue or malicious processes during investigations."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/kill_lab",
        "setup": [],
        "practice": (
            "Use 'kill -l' to list signals. "
            "Terminate a process gracefully with 'kill -15 <pid>' or force with 'kill -9 <pid>'."
        )
    },
    "pkill": {
        "brief": "Send signals to processes by name",
        "usage": "pkill [options] pattern",
        "options": {
            "-f": "Match full command line",
            "-u": "Match processes by user",
            "-n": "Send signal to newest matching process"
        },
        "ethical": (
            "Allows flexible process termination and management based on process attributes."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/pkill_lab",
        "setup": [],
        "practice": (
            "Use 'pkill -f python' to kill processes matching 'python' anywhere in the command line. "
            "Send signals to processes owned by a user with '-u'. "
            "Target newest process with '-n'."
        )
    },
    "jobs": {
        "brief": "List current shell background jobs",
        "usage": "jobs [options]",
        "options": {
            "-l": "Display PID with job",
            "-p": "Only print process IDs",
            "-r": "List running jobs only"
        },
        "ethical": (
            "Manage and monitor background tasks and jobs during sessions."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/jobs_lab",
        "setup": [],
        "practice": (
            "Run background jobs, then use 'jobs' to list them. "
            "Use '-l' to show process IDs. "
            "Use '-p' to just print PIDs and '-r' for running jobs."
        )
    },
    "fg": {
        "brief": "Bring background job to foreground",
        "usage": "fg %[job_number]",
        "options": {
            "--help": "Show help information"
        },
        "ethical": (
            "Useful for managing job control in shell sessions."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/fg_lab",
        "setup": [],
        "practice": (
            "Run a job in background using '&', list jobs with 'jobs', "
            "bring specific job to foreground using 'fg %1' (replace 1 with job number)."
        )
    },
    "history": {
        "brief": "Show command history",
        "usage": "history [options]",
        "options": {
            "-c": "Clear history",
            "-w": "Write history to file",
            "-r": "Read history from file"
        },
        "ethical": (
            "Helps in auditing past commands and cleaning traces."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/history_lab",
        "setup": [],
        "practice": (
            "View history with 'history'. "
            "Clear history with 'history -c'. "
            "Write and read history with '-w' and '-r' options."
        )
    },
    "alias": {
        "brief": "Create or list shell aliases",
        "usage": "alias [name='command']",
        "options": {
            "-p": "Print all aliases",
            "name='cmd'": "Create alias",
            "unalias": "Remove an alias"
        },
        "ethical": (
            "Aliases optimize workflow and can hide or shortcut commands."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/alias_lab",
        "setup": [],
        "practice": (
            "Create an alias with 'alias ll=\"ls -l\"'. "
            "List aliases with 'alias -p'. "
            "Remove an alias with 'unalias ll'."
        )
    },
    "grep": {
        "brief": "Search text in files",
        "usage": "grep [options] pattern [file...]",
        "options": {
            "-r": "Recursive search",
            "-i": "Case insensitive search",
            "-n": "Show line numbers"
        },
        "ethical": (
            "Essential for searching logs and output for relevant information."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/grep_lab",
        "setup": ["file1.txt"],
        "practice": (
            "Search for 'error' in 'file1.txt' using 'grep error file1.txt'. "
            "Search recursively in directories with '-r'. "
            "Ignore case with '-i' and show line numbers with '-n'."
        )
    },
    "find": {
        "brief": "Search for files in directory hierarchy",
        "usage": "find [path] [options]",
        "options": {
            "-name": "Search files by name",
            "-type": "Filter by file type (f=file, d=directory)",
            "-exec": "Execute command on found files"
        },
        "ethical": (
            "Useful to locate sensitive files and perform batch operations during audits."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/find_lab",
        "setup": ["file1.txt", "dir1/", "dir1/file2.txt"],
        "practice": (
            "Find files named 'file1.txt' using 'find . -name file1.txt'. "
            "Search directories with '-type d', files with '-type f'. "
            "Use '-exec' to run commands on found files, e.g., 'find . -name \"*.txt\" -exec cat {} \\;'."
        )
    },
    "locate": {
        "brief": "Quickly find files using a pre-built database",
        "usage": "locate [options] pattern",
        "options": {
            "-i": "Ignore case distinctions",
            "-r": "Use regex to match file names",
            "--limit": "Limit number of results returned"
        },
        "ethical": (
            "Provides fast file location to aid in quick reconnaissance."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/locate_lab",
        "setup": ["example.txt", "TestFile.TXT"],
        "practice": (
            "Use 'locate example.txt' to find files. "
            "Try ignoring case with '-i'. "
            "Use '-r' with regex patterns to refine searches. "
            "Limit results using '--limit N'."
        )
    },
    "sed": {
        "brief": "Stream editor for filtering and transforming text",
        "usage": "sed [options] script [file]",
        "options": {
            "-n": "Suppress automatic printing",
            "-i": "Edit files in-place",
            "-e": "Add script to execute"
        },
        "ethical": (
            "Key tool for automated text processing and log manipulation."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/sed_lab",
        "setup": ["file1.txt"],
        "practice": (
            "Print lines matching pattern using 'sed -n \"/pattern/p\" file1.txt'. "
            "Edit file in-place with '-i'. "
            "Execute multiple commands with '-e'."
        )
    },
    "awk": {
        "brief": "Powerful text processing and pattern scanning",
        "usage": "awk [options] 'script' [file]",
        "options": {
            "-F": "Set input field separator",
            "-v": "Assign variable value",
            "-f": "Execute script file"
        },
        "ethical": (
            "Enable complex text analysis and report generation during audits."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/awk_lab",
        "setup": ["file1.txt"],
        "practice": (
            "Print second column from 'file1.txt' with 'awk -F \",\" \"{print $2}\" file1.txt'. "
            "Assign variables using '-v var=value'. "
            "Run scripts from file with '-f script.awk'."
        )
    },
    "sort": {
        "brief": "Sort lines of text files",
        "usage": "sort [options] [file]",
        "options": {
            "-n": "Sort numerically",
            "-r": "Reverse sort order",
            "-u": "Unique lines only"
        },
        "ethical": (
            "Sorting output helps in analysis, deduplication, and report organization."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/sort_lab",
        "setup": ["file1.txt"],
        "practice": (
            "Sort text numerically with 'sort -n file1.txt'. "
            "Reverse sorting with '-r'. "
            "Get unique sorted lines with '-u'."
        )
    },
    "uniq": {
        "brief": "Filter adjacent matching lines",
        "usage": "uniq [options] [input [output]]",
        "options": {
            "-c": "Prefix lines by count",
            "-u": "Only unique lines",
            "-d": "Only duplicate lines"
        },
        "ethical": (
            "Useful for filtering and counting duplicates in logs or data."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/uniq_lab",
        "setup": ["file1.txt"],
        "practice": (
            "Count repeated lines using 'uniq -c file1.txt'. "
            "Print only unique lines with '-u'. "
            "Show duplicates only with '-d'."
        )
    },
    "wc": {
        "brief": "Count lines, words, and bytes",
        "usage": "wc [options] file",
        "options": {
            "-l": "Count lines",
            "-w": "Count words",
            "-c": "Count bytes"
        },
        "ethical": (
            "Counting data dimensions aids in data assessment and reporting."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/wc_lab",
        "setup": ["file1.txt"],
        "practice": (
            "Count lines in a file with 'wc -l file1.txt'. "
            "Count words with '-w' and bytes with '-c'."
        )
    },
    "tar": {
        "brief": "Archive files into tarballs",
        "usage": "tar [options] archive.tar [files]",
        "options": {
            "-c": "Create archive",
            "-x": "Extract archive",
            "-f": "Specify archive file"
        },
        "ethical": (
            "Archiving is useful for data backup and transfer during testing."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/tar_lab",
        "setup": ["file1.txt", "file2.txt"],
        "practice": (
            "Create archive: 'tar -cf archive.tar file1.txt file2.txt'. "
            "Extract archive: 'tar -xf archive.tar'."
        )
    },
    "gzip": {
        "brief": "Compress or decompress files",
        "usage": "gzip [options] file",
        "options": {
            "-d": "Decompress file",
            "-k": "Keep original file",
            "-c": "Write output to stdout"
        },
        "ethical": (
            "Compression helps manage storage and transfer efficiency."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/gzip_lab",
        "setup": ["file1.txt"],
        "practice": (
            "Compress 'file1.txt' with 'gzip file1.txt'. "
            "Decompress with 'gzip -d file1.txt.gz'. "
            "Keep original file with '-k'."
        )
    },
    "zip": {
        "brief": "Create compressed ZIP archives",
        "usage": "zip [options] zipfile files...",
        "options": {
            "-r": "Recursively include directories",
            "-q": "Quiet mode, suppress output",
            "-l": "List archived files"
        },
        "ethical": (
            "Compressing files reduces storage and facilitates data transfer during engagements."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/zip_lab",
        "setup": ["file1.txt", "dir1/"],
        "practice": (
            "Create a zip archive of a directory recursively using 'zip -r archive.zip dir1'. "
            "List contents of zip file using 'zip -l archive.zip'. "
            "Use '-q' for quiet execution."
        )
    },
    "df": {
        "brief": "Report disk space usage of file systems",
        "usage": "df [options]",
        "options": {
            "-h": "Human-readable sizes",
            "-T": "Show filesystem type",
            "-i": "Report inode usage"
        },
        "ethical": (
            "Disk space monitoring helps avoid system issues during testing."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/df_lab",
        "setup": [],
        "practice": (
            "Run 'df -h' to see disk space in human-readable format. "
            "Check filesystem types with '-T'. "
            "View inode usage with '-i'."
        )
    },
    "du": {
        "brief": "Estimate file and directory space usage",
        "usage": "du [options] [file/directory]",
        "options": {
            "-sh": "Summarize in human-readable format",
            "-h": "Human-readable sizes",
            "--max-depth": "Limit directory depth shown"
        },
        "ethical": (
            "Analyzing disk usage aids in resource optimization."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/du_lab",
        "setup": ["dir1/"],
        "practice": (
            "Summarize directory size using 'du -sh dir1'. "
            "Display sizes in human-readable form with '-h'. "
            "Control recursion depth with '--max-depth=N'."
        )
    },
    "free": {
        "brief": "Display system memory usage",
        "usage": "free [options]",
        "options": {
            "-h": "Human-readable output",
            "-m": "Show memory in megabytes",
            "-g": "Show memory in gigabytes"
        },
        "ethical": (
            "Memory usage insight assists in performance assessments and troubleshooting."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/free_lab",
        "setup": [],
        "practice": (
            "View memory usage in human-readable form with 'free -h'. "
            "Use '-m' or '-g' to display in MB or GB respectively."
        )
    },
    "ssh": {
        "brief": "Securely connect to remote hosts",
        "usage": "ssh [options] user@host",
        "options": {
            "-i": "Identity (private key) file",
            "-p": "Specify port",
            "-v": "Verbose mode for debugging"
        },
        "ethical": (
            "Essential for secure remote access and penetration efforts."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/ssh_lab",
        "setup": [],
        "practice": (
            "Connect using a private key with 'ssh -i keyfile.pem user@host'. "
            "Connect using non-default port with '-p PORT'. "
            "Use '-v' to debug connection issues."
        )
    },
    "scp": {
        "brief": "Securely copy files between hosts",
        "usage": "scp [options] source target",
        "options": {
            "-r": "Copy directories recursively",
            "-P": "Specify port",
            "-i": "Identity (private key) file"
        },
        "ethical": (
            "Secure file transfer helps maintain data confidentiality."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/scp_lab",
        "setup": ["file1.txt"],
        "practice": (
            "Copy files securely with 'scp file1.txt user@host:/path/'. "
            "Copy directories recursively with '-r'. "
            "Specify port with '-P' and identity file with '-i'."
        )
    },
    "ssh-keygen": {
        "brief": "Generate SSH key pairs",
        "usage": "ssh-keygen [options]",
        "options": {
            "-t": "Specify key type (e.g., rsa, ed25519)",
            "-b": "Set bits in key (key size)",
            "-f": "Specify output file"
        },
        "ethical": (
            "Generating keys is crucial for secure authentication during remote logins."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/ssh-keygen_lab",
        "setup": [],
        "practice": (
            "Generate a new SSH key pair with 'ssh-keygen -t rsa -b 2048 -f mykey'. "
            "Experiment with different key types and sizes."
        )
    },
    "curl": {
        "brief": "Transfer data from URLs",
        "usage": "curl [options] URL",
        "options": {
            "-I": "Fetch HTTP headers only",
            "-s": "Silent mode (no progress output)",
            "-o": "Write output to file"
        },
        "ethical": (
            "Vital for interacting with web services and APIs in testing."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/curl_lab",
        "setup": [],
        "practice": (
            "Fetch HTTP headers with 'curl -I http://example.com'. "
            "Download content silently with '-s'. "
            "Save output to file using '-o filename'."
        )
    },
    "wget": {
        "brief": "Download files from web",
        "usage": "wget [options] URL",
        "options": {
            "-O": "Write output to specified file",
            "-c": "Resume interrupted downloads",
            "-q": "Quiet mode"
        },
        "ethical": (
            "Automates retrieval of resources during penetration and auditing."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/wget_lab",
        "setup": [],
        "practice": (
            "Download a file with 'wget http://example.com/file'. "
            "Save to a specific file with '-O filename'. "
            "Resume downloads with '-c'. Use '-q' to suppress output."
        )
    },
    "ncat": {
        "brief": "Network utility for reading/writing data across networks",
        "usage": "ncat [options] hostname port",
        "options": {
            "-l": "Listen mode for inbound connections",
            "-p": "Local port number",
            "-e": "Execute program after connection"
        },
        "ethical": (
            "Essential for setting up remote shells, relay, or port forwarding."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/ncat_lab",
        "setup": [],
        "practice": (
            "Start a listener on a port with 'ncat -l -p 1234'. "
            "Connect to another machine with 'ncat hostname port'. "
            "Execute a shell upon connection with '-e /bin/bash'."
        )
    },
    "systemctl": {
        "brief": "Control and manage system services",
        "usage": "systemctl [command] [service]",
        "options": {
            "start": "Start a service",
            "stop": "Stop a service",
            "status": "Show status of a service"
        },
        "ethical": (
            "Managing services is essential for controlling system behavior and security."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/systemctl_lab",
        "setup": [],
        "practice": (
            "Check status of a service with 'systemctl status sshd'. "
            "Start a stopped service with 'systemctl start sshd'. "
            "Stop a running service with 'systemctl stop sshd'."
        )
    },
    "journalctl": {
        "brief": "Query systemd journal logs",
        "usage": "journalctl [options]",
        "options": {
            "-u": "Show logs for a specific service",
            "-f": "Follow log output live",
            "--since": "Show logs since a specific time"
        },
        "ethical": (
            "Accessing logs helps in auditing and troubleshooting system events."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/journalctl_lab",
        "setup": [],
        "practice": (
            "View logs of sshd service with 'journalctl -u sshd'. "
            "Follow live log updates with '-f'. "
            "Filter logs since yesterday with '--since yesterday'."
        )
    },
    "dmesg": {
        "brief": "Print kernel ring buffer messages",
        "usage": "dmesg [options]",
        "options": {
            "-T": "Print human-readable timestamps",
            "-w": "Wait for new messages (follow)",
            "--level": "Filter messages by log level"
        },
        "ethical": (
            "Reading kernel logs is crucial for diagnosing hardware and system issues."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/dmesg_lab",
        "setup": [],
        "practice": (
            "Display kernel messages with timestamps using 'dmesg -T'. "
            "Follow kernel messages live with '-w'. "
            "Filter messages by level, for example 'dmesg --level=err,warn'."
        )
    },
    "lsb_release": {
        "brief": "Show Linux distribution info",
        "usage": "lsb_release [options]",
        "options": {
            "-a": "Show all info",
            "-d": "Description of the distro",
            "-r": "Release version"
        },
        "ethical": (
            "Identifying system version is key for vulnerability assessment."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/lsb_release_lab",
        "setup": [],
        "practice": (
            "Display full distro info with 'lsb_release -a'. "
            "Get description only with '-d'. "
            "Show release version with '-r'."
        )
    },
    "hostnamectl": {
        "brief": "Control the system hostname",
        "usage": "hostnamectl [command]",
        "options": {
            "status": "Show current hostname settings",
            "set-hostname": "Set the system hostname",
            "--static": "Get or set the static hostname"
        },
        "ethical": (
            "Managing hostname is important for network identification."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/hostnamectl_lab",
        "setup": [],
        "practice": (
            "View hostname info with 'hostnamectl status'. "
            "Change hostname using 'hostnamectl set-hostname newname'. "
            "Check static hostname with '--static'."
        )
    },
    "apt": {
        "brief": "Package management tool for Debian-based systems",
        "usage": "apt [command]",
        "options": {
            "update": "Refresh package lists",
            "install": "Install packages",
            "upgrade": "Upgrade installed packages"
        },
        "ethical": (
            "Package management is essential for system maintenance and software deployment."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/apt_lab",
        "setup": [],
        "practice": (
            "Update package list with 'sudo apt update'. "
            "Install a package like 'curl' with 'sudo apt install curl'. "
            "Upgrade all packages using 'sudo apt upgrade'."
        )
    },
    "apt-get": {
        "brief": "Lower-level package management utility",
        "usage": "apt-get [command]",
        "options": {
            "update": "Update package lists",
            "install": "Install packages",
            "remove": "Remove packages"
        },
        "ethical": (
            "Widely used for scripting and automated package installs/removals."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/apt-get_lab",
        "setup": [],
        "practice": (
            "Run 'sudo apt-get update' to refresh. "
            "Install packages with 'sudo apt-get install packagename'. "
            "Remove packages with 'sudo apt-get remove packagename'."
        )
    },
    "dpkg": {
        "brief": "Debian package manager utility",
        "usage": "dpkg [options] package_file",
        "options": {
            "-i": "Install package",
            "-l": "List installed packages",
            "-r": "Remove package"
        },
        "ethical": (
            "Manages individual package files for fine-grained control."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/dpkg_lab",
        "setup": [],
        "practice": (
            "Install package with 'sudo dpkg -i package.deb'. "
            "List installed packages using 'dpkg -l'. "
            "Remove packages using 'dpkg -r packagename'."
        )
    },
    "snap": {
        "brief": "Manage snap packages",
        "usage": "snap [command]",
        "options": {
            "install": "Install snap packages",
            "remove": "Remove snap packages",
            "list": "List installed snaps"
        },
        "ethical": (
            "Snap packages provide containerized app management for modern Linux."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/snap_lab",
        "setup": [],
        "practice": (
            "Install snaps with 'sudo snap install packagename'. "
            "Remove a snap with 'sudo snap remove packagename'. "
            "List installed snaps using 'snap list'."
        )
    },
    "dnf": {
        "brief": "Package manager for Fedora-based systems",
        "usage": "dnf [command]",
        "options": {
            "install": "Install packages",
            "update": "Update packages",
            "remove": "Remove packages"
        },
        "ethical": (
            "Essential package management tool on Fedora and RHEL-based distros."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/dnf_lab",
        "setup": [],
        "practice": (
            "Install packages with 'sudo dnf install packagename'. "
            "Update system with 'sudo dnf update'. "
            "Remove packages using 'sudo dnf remove packagename'."
        )
    },
    "pacman": {
        "brief": "Package manager for Arch Linux",
        "usage": "pacman [options] packages",
        "options": {
            "-S": "Install packages",
            "-R": "Remove packages",
            "-Ss": "Search for packages in repositories"
        },
        "ethical": (
            "Installing and removing software is essential for system maintenance and testing."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/pacman_lab",
        "setup": [],
        "practice": (
            "Install a package using 'pacman -S package_name'. "
            "Search packages with 'pacman -Ss package_name'. "
            "Remove packages using 'pacman -R package_name'."
        )
    },
    "adduser": {
        "brief": "Add user with friendly defaults",
        "usage": "adduser [options] username",
        "options": {
            "--disabled-password": "Create user without password",
            "--gecos": "Set user info (name, room, phone)",
            "--ingroup": "Add user to specific group"
        },
        "ethical": (
            "User management is critical for controlling system access."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/adduser_lab",
        "setup": [],
        "practice": (
            "Create a user with no password: 'adduser --disabled-password testuser'. "
            "Set user info with '--gecos'. "
            "Add user to group with '--ingroup'."
        )
    },
    "useradd": {
        "brief": "Low-level user creation utility",
        "usage": "useradd [options] username",
        "options": {
            "-m": "Create home directory",
            "-s": "Set login shell",
            "-G": "Add to groups"
        },
        "ethical": (
            "Provides precise user account control for system security."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/useradd_lab",
        "setup": [],
        "practice": (
            "Create user with a home directory using 'useradd -m user1'. "
            "Specify shell with '-s'. "
            "Add user to supplementary groups with '-G'."
        )
    },
    "userdel": {
        "brief": "Delete user accounts",
        "usage": "userdel [options] username",
        "options": {
            "-r": "Remove home directory and mail spool",
            "-f": "Force deletion",
            "--help": "Show help message"
        },
        "ethical": (
            "Removing users helps maintain system hygiene and security."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/userdel_lab",
        "setup": [],
        "practice": (
            "Delete user with home using 'userdel -r user1'. "
            "Force removal with '-f'. "
            "View help with '--help'."
        )
    },
    "groupadd": {
        "brief": "Create new groups",
        "usage": "groupadd [options] groupname",
        "options": {
            "-g": "Set group ID",
            "-r": "Create system group",
            "--help": "Display help"
        },
        "ethical": (
            "Group creation supports user access organization."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/groupadd_lab",
        "setup": [],
        "practice": (
            "Create group with default ID: 'groupadd mygroup'. "
            "Set specific GID with '-g'. "
            "Create system groups with '-r'."
        )
    },
    "passwd": {
        "brief": "Change user password and lock/unlock accounts",
        "usage": "passwd [options] [username]",
        "options": {
            "-l": "Lock account",
            "-u": "Unlock account",
            "--expire": "Expire password immediately"
        },
        "ethical": (
            "Password management is crucial for user security."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/passwd_lab",
        "setup": [],
        "practice": (
            "Lock user account with 'passwd -l username'. "
            "Unlock it with '-u'. "
            "Expire password forcing reset with '--expire'."
        )
    },
    "su": {
        "brief": "Switch user",
        "usage": "su [options] [username]",
        "options": {
            "-": "Login shell for target user",
            "-c": "Execute command as another user"
        },
        "ethical": (
            "User switching allows privilege escalation or testing."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/su_lab",
        "setup": [],
        "practice": (
            "Switch to another user shell with 'su - username'. "
            "Run commands as another user with 'su -c \"command\" username'."
        )
    },
    "crontab": {
        "brief": "Manage user cron jobs",
        "usage": "crontab [options]",
        "options": {
            "-e": "Edit crontab",
            "-l": "List crontab",
            "-r": "Remove crontab"
        },
        "ethical": (
            "Cron jobs automate tasks, important for system maintenance."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/crontab_lab",
        "setup": [],
        "practice": (
            "Edit crontab with 'crontab -e'. "
            "List scheduled jobs with '-l'. "
            "Remove crontab with '-r'."
        )
    },
    "at": {
        "brief": "Schedule commands to run once",
        "usage": "at [options] time",
        "options": {
            "-f": "Read commands from file",
            "-l": "List pending jobs",
            "-q": "Select job queue"
        },
        "ethical": (
            "Scheduled tasks allow controlled execution at specific times."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/at_lab",
        "setup": [],
        "practice": (
            "Schedule commands with 'echo \"ls\" | at now + 1 minute'. "
            "List jobs with 'at -l'. "
            "Run script files with '-f'."
        )
    },
    "systemd-run": {
        "brief": "Run commands as transient systemd units",
        "usage": "systemd-run [options] command",
        "options": {
            "--unit": "Specify unit name",
            "--property": "Set unit properties",
            "--slice": "Assign to systemd slice"
        },
        "ethical": (
            "Manage transient services for controlled resource use."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/systemd-run_lab",
        "setup": [],
        "practice": (
            "Run a command as a service with 'systemd-run --unit=myjob sleep 60'. "
            "Set unit properties with '--property'. "
            "Assign the job to a slice with '--slice'."
        )
    },
    "openssl": {
        "brief": "Toolkit for SSL/TLS and cryptography",
        "usage": "openssl command [options]",
        "options": {
            "s_client": "Test SSL/TLS client connections",
            "req": "Create and process certificate requests",
            "x509": "Certificate display and signing"
        },
        "ethical": (
            "Key tool for managing cryptographic keys and secure communications."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/openssl_lab",
        "setup": [],
        "practice": (
            "Test TLS connection with 'openssl s_client -connect example.com:443'. "
            "Generate CSR with 'openssl req -new -newkey rsa:2048 -nodes -keyout key.pem -out req.csr'. "
            "Create self-signed certificate with 'openssl x509 -req -days 365 -in req.csr -signkey key.pem -out cert.pem'."
        )
    },
    "gpg": {
        "brief": "Encrypt and sign files",
        "usage": "gpg [options]",
        "options": {
            "--encrypt": "Encrypt data",
            "--decrypt": "Decrypt data",
            "--list-keys": "List keys in keyring"
        },
        "ethical": (
            "Encryption tool vital for secure communication and verification."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/gpg_lab",
        "setup": ["file1.txt"],
        "practice": (
            "Encrypt 'file1.txt' with 'gpg --encrypt -r user_id file1.txt'. "
            "Decrypt encrypted files with '--decrypt'. "
            "List keys using '--list-keys'."
        )
    },
    "chattr": {
        "brief": "Change file attributes on ext file systems",
        "usage": "chattr [options] file",
        "options": {
            "+i": "Make file immutable",
            "-i": "Remove immutable flag",
            "-R": "Recursively apply to directories"
        },
        "ethical": (
            "Protects files from accidental or malicious modification."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/chattr_lab",
        "setup": ["file1.txt", "dir1/"],
        "practice": (
            "Make 'file1.txt' immutable with 'chattr +i file1.txt'. "
            "Remove immutability with '-i'. "
            "Apply changes recursively to directories with '-R'."
        )
    },
    "lsblk": {
        "brief": "List information about block devices",
        "usage": "lsblk [options]",
        "options": {
            "-f": "Show filesystem info",
            "-a": "Show all devices",
            "-o": "Specify output columns"
        },
        "ethical": (
            "Displays storage device details critical for forensic and system analysis."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/lsblk_lab",
        "setup": [],
        "practice": (
            "List block devices with 'lsblk'. "
            "Show filesystem info using '-f'. "
            "Display all devices with '-a' and customize output columns with '-o'."
        )
    },
    "fdisk": {
        "brief": "Partition table manipulator for block devices",
        "usage": "fdisk [options] device",
        "options": {
            "-l": "List partition tables",
            "-u": "Display sectors in units",
            "-s": "Report partition size in blocks"
        },
        "ethical": (
            "Crucial for managing disk partitions and recovery tasks."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/fdisk_lab",
        "setup": [],
        "practice": (
            "List partitions on devices with 'fdisk -l'. "
            "Use '-u' to control unit display. "
            "Report partition sizes with '-s'."
        )
    },
    "mkfs": {
        "brief": "Create a filesystem on a device",
        "usage": "mkfs [options] device",
        "options": {
            "-t": "Filesystem type (ext4, xfs, etc.)",
            "-V": "Show version info",
            "-n": "Set volume name"
        },
        "ethical": (
            "Used to prepare storage for data; careful usage prevents data loss."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/mkfs_lab",
        "setup": [],
        "practice": (
            "Create an ext4 filesystem with 'mkfs -t ext4 /dev/sdx1'. "
            "View mkfs version with '-V'. "
            "Label filesystem volume with '-n'."
        )
    },
    "mount": {
        "brief": "Mount filesystems",
        "usage": "mount [options] device dir",
        "options": {
            "-t": "Specify filesystem type",
            "-o": "Specify mount options",
            "-a": "Mount all filesystems in fstab"
        },
        "ethical": (
            "Mounting devices is essential for accessing storage and forensic analysis."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/mount_lab",
        "setup": [],
        "practice": (
            "Mount a device with 'mount -t ext4 /dev/sdx1 /mnt'. "
            "Use '-o' for options like 'ro' (read-only). "
            "Mount all filesystems in fstab with '-a'."
        )
    },
    "umount": {
        "brief": "Unmount filesystems",
        "usage": "umount [options] device_or_dir",
        "options": {
            "-a": "Unmount all",
            "-f": "Force unmount",
            "-l": "Lazy unmount"
        },
        "ethical": (
            "Unmounting ensures safe removal and maintenance of storage devices."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/umount_lab",
        "setup": [],
        "practice": (
            "Unmount a device with 'umount /mnt'. "
            "Force unmount with '-f'. "
            "Use lazy unmount with '-l' for delayed detachment."
        )
    },
    "blkid": {
        "brief": "Display block device attributes",
        "usage": "blkid [options]",
        "options": {
            "-o": "Output format",
            "-s": "Print specific attribute",
            "-p": "Probe devices"
        },
        "ethical": (
            "Useful to identify device UUIDs and labels for system configuration."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/blkid_lab",
        "setup": [],
        "practice": (
            "List all devices with UUIDs using 'blkid'. "
            "Print specific attributes with '-s'. "
            "Probe devices with '-p'."
        )
    },
    "ln": {
        "brief": "Create links between files",
        "usage": "ln [options] target link_name",
        "options": {
            "-s": "Create symbolic link",
            "-f": "Force overwrite existing files",
            "-n": "Do not dereference symlinks"
        },
        "ethical": (
            "Links are used to organize files and create shortcuts."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/ln_lab",
        "setup": ["file1.txt"],
        "practice": (
            "Create symbolic link with 'ln -s file1.txt link1'. "
            "Force overwrite existing links with '-f'. "
            "Use '-n' to prevent dereferencing symlinks."
        )
    },
    "rsync": {
        "brief": "Remote and local file synchronization",
        "usage": "rsync [options] source destination",
        "options": {
            "-avz": "Archive mode, verbose, compress data",
            "--delete": "Delete files in destination not in source",
            "-P": "Show progress and allow resuming transfers"
        },
        "ethical": (
            "Used for efficient backups, mirroring, and secure file transfers."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/rsync_lab",
        "setup": ["file1.txt", "dir1/"],
        "practice": (
            "Sync 'dir1' to 'backup_dir' using 'rsync -avz dir1 backup_dir'. "
            "Try '--delete' to remove extraneous files from destination. "
            "Use '-P' to see progress and resume interrupted transfers."
        )
    },
    "sftp": {
        "brief": "Interact with remote file servers over SSH",
        "usage": "sftp [options] [user@]host",
        "options": {
            "-o": "Pass SSH options",
            "-b": "Batch mode, run commands from file",
            "-P": "Specify port"
        },
        "ethical": (
            "Securely transfer files over encrypted connections."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/sftp_lab",
        "setup": [],
        "practice": (
            "Connect to a host using 'sftp user@host'. "
            "Use '-P' to specify a port. "
            "Batch upload/download files using '-b batchfile'."
        )
    },
    "git": {
        "brief": "Distributed version control system",
        "usage": "git [command]",
        "options": {
            "clone": "Copy a repository",
            "pull": "Update local repo from remote",
            "commit": "Record changes to repository"
        },
        "ethical": (
            "Version control helps track and manage code changes securely."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/git_lab",
        "setup": [],
        "practice": (
            "Clone a public repo with 'git clone URL'. "
            "Pull updates with 'git pull'. "
            "Commit changes locally with 'git commit -m \"message\"'."
        )
    },
    "docker": {
        "brief": "Container platform for applications",
        "usage": "docker [command]",
        "options": {
            "run": "Run a new container instance",
            "ps": "List running containers",
            "exec": "Execute commands inside containers"
        },
        "ethical": (
            "Containers isolate apps; managing them is key in modern infrastructures."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/docker_lab",
        "setup": [],
        "practice": (
            "Run a container: 'docker run -it ubuntu bash'. "
            "List containers with 'docker ps'. "
            "Execute commands inside a container using 'docker exec -it container_id bash'."
        )
    },
    "systemd-analyze": {
        "brief": "Analyze system boot performance",
        "usage": "systemd-analyze [command]",
        "options": {
            "blame": "Show time taken by each service",
            "plot": "Generate SVG graph of boot process",
            "time": "Show total boot time"
        },
        "ethical": (
            "Helps diagnose slow boots and improve system responsiveness."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/systemd-analyze_lab",
        "setup": [],
        "practice": (
            "Show time each service takes with 'systemd-analyze blame'. "
            "Create graph with 'systemd-analyze plot > boot.svg'. "
            "View total boot time with 'systemd-analyze time'."
        )
    },
    "watch": {
        "brief": "Run a command repeatedly and show output",
        "usage": "watch [options] command",
        "options": {
            "-n": "Interval seconds between updates",
            "-d": "Highlight changes",
            "-t": "Disable header"
        },
        "ethical": (
            "Useful for monitoring changing command outputs in real-time."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/watch_lab",
        "setup": [],
        "practice": (
            "Monitor disk usage every 2 seconds: 'watch -n 2 df -h'. "
            "Highlight changes with '-d'. "
            "Disable header with '-t'."
        )
    },
    "tee": {
        "brief": "Read from standard input and write to files and stdout",
        "usage": "tee [options] file...",
        "options": {
            "-a": "Append to files",
            "-i": "Ignore interrupts",
            "--help": "Show help"
        },
        "ethical": (
            "Captures output while allowing it to pass downstream."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/tee_lab",
        "setup": [],
        "practice": (
            "Save output and display: 'ls | tee output.txt'. "
            "Append output with '-a'. "
            "Ignore interrupts with '-i'."
        )
    },
    "xargs": {
        "brief": "Build and execute command lines from input",
        "usage": "xargs [options] command",
        "options": {
            "-n": "Use specified number of arguments per command invocation",
            "-I": "Replace string in command with input line",
            "-0": "Input items are null-terminated"
        },
        "ethical": (
            "Processes output efficiently for scripting and automation."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/xargs_lab",
        "setup": [],
        "practice": (
            "Use 'echo list | xargs -n 1 echo' to process one argument per command. "
            "Replace placeholder with '-I {}'. "
            "Use with null-terminated input via '-0'."
        )
    },
    "timeout": {
        "brief": "Run command with time limit",
        "usage": "timeout [options] duration command",
        "options": {
            "-s": "Send a signal on timeout",
            "-k": "Kill after delay if command ignores signal",
            "--preserve-status": "Exit with command's exit status"
        },
        "ethical": (
            "Prevents runaway processes in scripts and tests."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/timeout_lab",
        "setup": [],
        "practice": (
            "Run command for 10 seconds: 'timeout 10 ping google.com'. "
            "Send specific signal with '-s'. "
            "Force kill with '-k'."
        )
    },
    "env": {
        "brief": "Run command in modified environment",
        "usage": "env [options] [name=value] command",
        "options": {
            "-i": "Start with empty environment",
            "-u": "Remove variable from environment",
            "--help": "Show help"
        },
        "ethical": (
            "Controls environment variables, aiding controlled executions."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/env_lab",
        "setup": [],
        "practice": (
            "Run command with clean environment: 'env -i bash'. "
            "Remove variables with '-u'. "
            "View help with '--help'."
        )
    },
    "printenv": {
        "brief": "Display environment variables",
        "usage": "printenv [VAR]",
        "options": {
            "-0": "Use null character as delimiter",
            "--help": "Show help information",
            "VAR": "Print value of specified variable"
        },
        "ethical": (
            "Shows environment for troubleshooting and security checks."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/printenv_lab",
        "setup": [],
        "practice": (
            "Run 'printenv' to list all variables. "
            "Print a specific variable with 'printenv HOME'. "
            "Use '-0' to separate output with null characters."
        )
    },
    "basename": {
        "brief": "Extract filename from path",
        "usage": "basename [options] path",
        "options": {
            "--suffix": "Remove a suffix from the name",
            "--help": "Show help text",
            "-a": "Support multiple arguments"
        },
        "ethical": (
            "Useful for parsing and handling filenames in scripts."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/basename_lab",
        "setup": [],
        "practice": (
            "Get filename from '/path/to/file.txt' using 'basename /path/to/file.txt'. "
            "Remove suffix with '--suffix .txt'. "
            "Process multiple paths at once using '-a'."
        )
    },
    "dirname": {
        "brief": "Extract directory component from path",
        "usage": "dirname [options] path",
        "options": {
            "--help": "Show help",
            "--version": "Show version"
        },
        "ethical": (
            "Helpful for scripting to isolate directory names."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/dirname_lab",
        "setup": [],
        "practice": (
            "Extract directory from '/path/to/file.txt' with 'dirname /path/to/file.txt'. "
            "Use '--help' for help and '--version' for version info."
        )
    },
    "sshfs": {
        "brief": "Mount remote directories over SSH",
        "usage": "sshfs [options] user@host:/remote/dir /local/mount",
        "options": {
            "-o": "Pass mount options",
            "-p": "Port number for SSH",
            "-C": "Enable compression"
        },
        "ethical": (
            "Enables secure network file access for remote resources."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/sshfs_lab",
        "setup": [],
        "practice": (
            "Mount remote directory with 'sshfs user@host:/remote /mnt'. "
            "Use '-p' to specify SSH port, and '-C' to enable compression."
        )
    },
    "ufw": {
        "brief": "Uncomplicated Firewall management",
        "usage": "ufw [command]",
        "options": {
            "enable": "Enable firewall",
            "allow": "Allow connections",
            "status": "Show firewall status"
        },
        "ethical": (
            "Firewall configuration is critical for system security."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/ufw_lab",
        "setup": [],
        "practice": (
            "Enable firewall with 'sudo ufw enable'. "
            "Allow SSH with 'sudo ufw allow ssh'. "
            "Check status with 'sudo ufw status'."
        )
    },
    "iptables": {
        "brief": "Configure Linux kernel firewall",
        "usage": "iptables [options]",
        "options": {
            "-L": "List rules",
            "-A": "Append rule",
            "-F": "Flush all rules"
        },
        "ethical": (
            "Direct firewall control for detailed security policies."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/iptables_lab",
        "setup": [],
        "practice": (
            "List current rules with 'sudo iptables -L'. "
            "Append a rule with 'sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT'. "
            "Flush rules with 'sudo iptables -F'."
        )
    },
    "tcpdump": {
        "brief": "Capture network packets",
        "usage": "tcpdump [options]",
        "options": {
            "-i": "Specify interface",
            "-w": "Write packets to file",
            "-nn": "Do not resolve names"
        },
        "ethical": (
            "Network capture enables deep protocol and traffic analysis."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/tcpdump_lab",
        "setup": [],
        "practice": (
            "Capture packets on 'eth0' with 'sudo tcpdump -i eth0'. "
            "Write capture to file with '-w capture.pcap'. "
            "Disable DNS and port name resolution with '-nn'."
        )
    },
    "ncdu": {
        "brief": "Disk usage analyzer with ncurses interface",
        "usage": "ncdu [options] [directory]",
        "options": {
            "-x": "Stay on one filesystem",
            "-r": "Read-only mode",
            "-q": "Quiet mode"
        },
        "ethical": (
            "Useful for disk space auditing and cleanup."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/ncdu_lab",
        "setup": [],
        "practice": (
            "Run ncdu in directory with 'ncdu /path'. "
            "Use '-x' to ignore other filesystems. "
            "Try read-only mode with '-r'."
        )
    },
    "strace": {
        "brief": "Trace system calls and signals",
        "usage": "strace [options] command",
        "options": {
            "-p": "Attach to process by PID",
            "-f": "Follow child processes",
            "-o": "Write trace output to file"
        },
        "ethical": (
            "Diagnoses program behavior and vulnerabilities."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/strace_lab",
        "setup": [],
        "practice": (
            "Trace a new program with 'strace ls'. "
            "Attach to a running process with '-p PID'. "
            "Follow child processes with '-f', write to file with '-o trace.txt'."
        )
    },
    "lsof": {
        "brief": "List open files",
        "usage": "lsof [options]",
        "options": {
            "-i": "List network files",
            "-p": "List files by PID",
            "-nP": "Disable host and port name resolution"
        },
        "ethical": (
            "Identifies file and network usage for forensics and debugging."
        ),
        "lab_dir": "/tmp/linux_tutor_lab/lsof_lab",
        "setup": [],
        "practice": (
            "List all network connections with 'lsof -i'. "
            "List files opened by a process with '-p PID'. "
            "Disable name resolution for faster results with '-nP'."
        )
    }
}

# --------- Your command list (command, description) ----------
LINUX_COMMANDS = [
    ("ls", "list files"),
    ("pwd", "present directory"),
    ("mkdir", "make directory"),
    ("ls", "list files"),
    ("cd", "change directory"),
    ("touch", "update timestamps"),
    ("echo", "print text"),
    ("cat", "concatenate files"),
    ("less", "view file"),
    ("head", "file start"),
    ("tail", "file end"),
    ("cp", "copy files"),
    ("mv", "move files"),
    ("rm", "remove files"),
    ("rmdir", "remove directory"),
    ("file", "file type"),
    ("stat", "file status"),
    ("chmod", "change permissions"),
    ("chown", "change owner"),
    ("sudo", "run command"),
    ("whoami", "current user"),
    ("id", "user identity"),
    ("ps", "process status"),
    ("top", "process monitor"),
    ("htop", "interactive monitor"),
    ("kill", "terminate process"),
    ("pkill", "kill processes"),
    ("jobs", "background jobs"),
    ("fg", "foreground job"),
    ("history", "command history"),
    ("alias", "create shortcut"),
    ("grep", "pattern search"),
    ("find", "file search"),
    ("locate", "file finder"),
    ("sed", "stream editor"),
    ("awk", "text processing"),
    ("sort", "sort lines"),
    ("uniq", "unique lines"),
    ("wc", "word count"),
    ("tar", "archive files"),
    ("gzip", "compress files"),
    ("zip", "archive files"),
    ("df", "disk usage"),
    ("du", "disk usage"),
    ("free", "memory status"),
    ("ssh", "secure shell"),
    ("scp", "secure copy"),
    ("ssh-keygen", "generate keys"),
    ("curl", "transfer data"),
    ("wget", "download files"),
    ("ncat/nc", "network utility"),
    ("systemctl", "service management"),
    ("journalctl", "log viewer"),
    ("dmesg", "kernel messages"),
    ("lsb_release", "distro info"),
    ("hostnamectl", "hostname control"),
    ("apt", "package manager"),
    ("apt-get", "package manager"),
    ("dpkg", "package tool"),
    ("snap", "package manager"),
    ("dnf", "package manager"),
    ("pacman", "package manager"),
    ("adduser", "add user"),
    ("useradd", "create user"),
    ("userdel", "delete user"),
    ("groupadd", "add group"),
    ("passwd", "change password"),
    ("su", "switch user"),
    ("crontab", "schedule jobs"),
    ("at", "run once"),
    ("systemd-run", "execute service"),
    ("openssl", "crypto tools"),
    ("gpg", "encrypt decrypt"),
    ("chattr", "file attributes"),
    ("lsblk", "block devices"),
    ("fdisk", "disk partition"),
    ("mkfs", "make filesystem"),
    ("mount", "mount device"),
    ("umount", "unmount device"),
    ("blkid", "device id"),
    ("ln", "create links"),
    ("rsync", "sync files"),
    ("sftp", "file transfer"),
    ("git", "version control"),
    ("docker", "container tool"),
    ("systemd-analyze", "boot analysis"),
    ("watch", "command repeat"),
    ("tee", "redirect output"),
    ("xargs", "argument builder"),
    ("timeout", "limit time"),
    ("env", "environment variables"),
    ("printenv", "print environment"),
    ("basename", "file name"),
    ("dirname", "directory path"),
    ("sshfs", "remote filesystem"),
    ("ufw", "firewall manager"),
    ("iptables", "firewall rules"),
    ("tcpdump", "packet capture"),
    ("ncdu", "disk usage"),
    ("strace", "system calls"),
    ("lsof", "open files"),
]