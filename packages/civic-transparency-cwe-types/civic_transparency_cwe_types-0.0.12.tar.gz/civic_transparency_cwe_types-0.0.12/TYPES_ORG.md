src/
└── ci/
    └── transparency/
        └── cwe/
            # IMPORTANT: no __init__.py at these three shared levels
            └── types/                      # leaf package owned by this dist
                ├── __init__.py             # convenience re-exports; __version__
                ├── py.typed
                │
                ├── base/
                │   ├── collections.py
                │   ├── counts.py
                │   ├── errors.py
                │   ├── messages.py
                │   └── schema.py
                │
                ├── schema/                 # domain-neutral (instance↔schema)
                │   ├── results.py
                │   └── errors.py
                │
                ├── schema_evolution/       # domain-neutral (schema↔schema)
                │   ├── results.py
                │   └── errors.py
                │
                ├── cwe/                    # CWE-specific thin wrappers/adapters
                │   ├── results.py
                │   ├── errors.py
                │   └── schema/
                │       ├── results.py      # aliases/adapters of neutral types
                │       └── errors.py
                │
                └── standards/
                    ├── results.py
                    └── errors.py
