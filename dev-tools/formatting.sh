echo "Ruff"
ruff check src/

echo "Mypy"
python -m mypy src

echo "Pydocstyle"
pydocstyle src
if [ $? -eq 0 ]; then
    echo "Pydoctstyle passed!"
fi

for file in src/estafettes/*.py src/estafettes/brevo/*.py; do
    echo "Testing $file"
    python -m doctest "$file" -v
done