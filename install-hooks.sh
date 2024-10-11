#!/bin/sh

cd .git/hooks || exit $?

if [ ! -f pre-commit ]; then
  cat << 'EOF' > pre-commit
#!/bin/sh

ruff check convertool || exit $?
ruff format --check convertool || exit $?
EOF
  chmod +x pre-commit
fi

:
