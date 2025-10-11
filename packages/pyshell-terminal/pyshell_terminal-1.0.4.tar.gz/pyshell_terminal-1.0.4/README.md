# PyShell 🐚

A feature-rich, POSIX-compatible shell implemented in Python with advanced scripting capabilities.

## ✨ Features

- **POSIX Compatibility**: Standard shell syntax (if/while/for/case)
- **Advanced Arrays**: Indexed and associative arrays
- **Pipeline Support**: Full pipe, redirection, and background job control
- **Function Definitions**: Shell functions with local variables
- **Parameter Expansion**: Comprehensive variable expansion (`${var:-default}`, `${var#pattern}`, etc.)
- **Command Substitution**: `$(command)` and backtick syntax
- **Arithmetic Expansion**: `$((expression))` with full math operations
- **Brace Expansion**: `{1..10}`, `{a,b,c}`
- **Glob Patterns**: `*`, `?`, `[...]` with extended patterns
- **Built-in Commands**: 50+ built-ins including cd, echo, test, export, local, etc.
- **Job Control**: Background jobs with fg/bg commands
- **History & Completion**: Command history with readline integration
- **Aliases**: Command aliasing support
- **Cross-Platform**: Works on Linux, macOS, and Windows

## 🚀 Installation

### From Source

```bash
git clone https://github.com/yogvidwankhede/PyShell.git
cd pyshell
pip install -e .
```

### Using pip (once published)

```bash
pip install pyshell-terminal
```

## 📖 Usage

### Interactive Mode

```bash
python main.py
```

### Execute Command

```bash
python main.py -c "echo Hello World"
```

### Run Script

```bash
python main.py script.sh
```

## 💡 Examples

### Variables and Arrays

```bash
# Simple variables
name="PyShell"
echo $name

# Arrays
arr=(one two three)
echo ${arr[0]}
echo ${arr[@]}

# Associative arrays
declare -A config
config[host]="localhost"
config[port]=8080
echo ${config[host]}
```

### Control Flow

```bash
# If statements
if [ -f "file.txt" ]; then
    echo "File exists"
else
    echo "File not found"
fi

# Loops
for i in {1..5}; do
    echo "Count: $i"
done

# While loops
count=0
while [ $count -lt 5 ]; do
    echo $count
    count=$((count + 1))
done
```

### Functions

```bash
greet() {
    local name=$1
    echo "Hello, $name!"
}

greet "World"
```

### Pipelines and Redirection

```bash
# Pipes
cat file.txt | grep "pattern" | wc -l

# Redirection
echo "data" > output.txt
cat input.txt >> output.txt
command 2> errors.log
```

## 🏗️ Architecture

```
pyshell/
├── main.py           # Entry point and REPL
├── pyshell/
│   ├── tokenizer.py  # Lexical analysis
│   ├── parser.py     # Syntax analysis
│   ├── executor.py   # Command execution
│   ├── expansions.py # Variable/command expansion
│   ├── builtins.py   # Built-in commands
│   ├── state.py      # Global shell state
│   ├── ast_nodes.py  # AST node definitions
│   ├── exceptions.py # Custom exceptions
│   └── utils.py      # Utilities
└── tests/            # Test suite
```

## 🧪 Testing

```bash
python tests/run_all_tests.py
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 Roadmap

- [ ] Tab completion improvements
- [ ] More POSIX test operators
- [ ] Process substitution
- [ ] Co-processes
- [ ] Additional shell options
- [ ] Performance optimizations

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by Bash, Zsh, and other Unix shells
- Built with Python's readline and subprocess modules
