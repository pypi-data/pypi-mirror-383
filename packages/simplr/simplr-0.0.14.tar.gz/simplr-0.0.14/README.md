# simplr

A tool for running OS independent commands using natural language.  

Utilizes LLMs that understand folder structure and remembers previous commands to make context-aware decisions.

## Installation
```
python -m pip install simplr
```
## Usage
Run Simplr interactively:
```
simplr run
```

Launches an interactive CLI where you can type natural language commands, like:

```
simplr > start a local server on port 8000
simplr > compress all images in this folder
```

The CLI can also be used as a normal terminal.

Or run a single command directly:

```
simplr delete all .pyc files
```

Simplr will interpret and give selectable command options for user review before executing anything.

```
? C:\Users\User\Desktop >>> simplr > list all files in this directory
? Possible commands: (Use arrow keys)
 » dir
   dir /b
   dir /s
   Skip
```

## Additional Commands
| Syntax | Description |
| ----------- | ----------- |
| simplr clear_cache | Clears cache for current directory. |
| simplr config | Resets and reinitializes configuration settings. |

## Limitations

Since the commands are run in a subprocess, some edge cases around activating/deativating virtual environments, navigating folders, etc. may lead to unexpected results.
