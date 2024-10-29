#!/bin/sh

cd .git/hooks || exit $?

if [ ! -f pre-commit ]; then
  cat << 'EOF' > pre-commit
#!/bin/sh

ruff check || exit $?
ruff format --check || exit $?
EOF
  chmod +x pre-commit
fi

:
