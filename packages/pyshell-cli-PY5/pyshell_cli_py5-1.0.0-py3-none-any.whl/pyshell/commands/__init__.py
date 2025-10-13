"""
Commands module - Plugin directory for shell commands.
Each command is a separate Python module with a run(args, shell) function.

Available commands:
- cat: Concatenate and display file contents (with -n/-b/-s options)
<<<<<<< HEAD
- cp: Copy files and directories (with -r/-i/-u/-v options)
- ls: List directory contents
- mkdir: Create directories
- mv: Move/rename files and directories
=======
- cd: Change directory
- clear: Clear the terminal screen
- cp: Copy files and directories (with -r/-i/-u/-v options)
- find: Search for files in directory hierarchy
- grep: Search text patterns in files (with -i/-n/-v options)
- head: Output the first part of files (with -n option)
- ls: List directory contents (with -l/-a/-h options)
- mkdir: Create directories (with -p/-v options)
- mv: Move/rename files and directories (with -i/-v options)
>>>>>>> 3d936d67956d61628eec304b9f8e1639c857581e
- pwd: Print working directory (with -L/-P options)
- rm: Remove files and directories (with -r/-v/-i/-f options)
- rmdir: Remove empty directories
- sizeof: Display file size in bytes
- tail: Output the last part of files (with -n option)
"""

