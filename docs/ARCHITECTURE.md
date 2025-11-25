## Architecture

This project follows **Clean Architecture** (hexagonal/ports-and-adapters style) to keep business rules independent from frameworks and infrastructure.

Key principles:
- **Domain**: Pure business models and rules (entities, domain exceptions, repository interfaces). No framework code.
- **Application**: Use cases (interactors) that orchestrate domain entities and depend only on abstractions (ports). They accept input DTOs and return output DTOs.
- **Infrastructure**: Concrete adapters — database drivers, repositories, mappers, migration scripts, logging, configuration. Implements the domain ports.
- **Presentation**: Thin adapters (CLI) that map user input to application DTOs and present output; contains argument parsing, formatters, and command routing.

This separation improves testability, maintainability, and allows each layer to evolve independently.

---

## Project Structure


```
src/
└── raztodo/
    ├── application/
    │   └── use_cases/
    ├── domain/
    ├── infrastructure/
    │   └── sqlite/
    ├── presentation/
    │   └── cli/
    ├── __main__.py
```


---

### 1. Application Layer  
**Directory:** `application/`

The Application layer contains the operational logic of the system in the form of **Use Cases**, each defining a specific business operation.

#### `use_cases/`
Each file represents an isolated business action:

- `[create_task.py](https://github.com/razbuild/raztodo/src/raztodo/application/use_cases/create_task.py)` – Creates a new task with data validation  
- `[delete_task.py](/src/raztodo/application/use_cases/delete_task.py)` – Deletes a task by its ID  
- `[export_task.py](/src/raztodo/application/use_cases/export_task.py)` – Exports tasks to an external format  
- `[import_task.py](/src/raztodo/application/use_cases/import_task.py)` – Imports tasks from an external source  
- `[list_tasks.py](/src/raztodo/application/use_cases/list_tasks.py)` – Retrieves the full list of tasks  
- `[mark_task_done.py](/src/raztodo/application/use_cases/mark_task_done.py)` – Marks a task as completed  
- `[migrate_tasks.py](/src/raztodo/application/use_cases/migrate_tasks.py)` – Handles database migrations  
- `[search_tasks.py](/src/raztodo/application/use_cases/search_tasks.py)` – Searches for tasks by criteria  
- `[update_task.py](/src/raztodo/application/use_cases/update_task.py)` – Updates task details  

---

### 2. Domain Layer  
**Directory:** `domain/`

This layer contains the core business logic and entities, completely independent of external systems.

- `[task_entity.py](/src/raztodo/domain/task_entity.py)` – Domain model representing a Task  
- `[exceptions.py](/src/raztodo/domain/exceptions.py)` – Domain-specific exceptions  
- `[task_repository.py](/src/raztodo/domain/task_repository.py)` – Repository interface defining the storage contract  

---

### 3. Infrastructure Layer  
**Directory:** `infrastructure/`

Contains concrete implementations of repositories, storage, configuration, and various services.

#### Key Files
- `[container.py](../src/raztodo/infrastructure/container.py)` – Dependency injection and service wiring  
- `[logger.py](/src/raztodo/infrastructure/logger.py)` – Logging configuration  
- `[settings.py](/src/raztodo/infrastructure/settings.py)` – Configuration loading and environment settings  

#### `sqlite/`
SQLite-based backend implementation:

- `[connection.py](../src/raztodo/infrastructure/sqlite/connection.py)` – SQLite connection manager  
- `[task_schema.py](/src/raztodo/infrastructure/sqlite/task_schema.py)` – Database schema definitions  
- `[migrations.py](/src/raztodo/infrastructure/sqlite/migrations.py)` – Database migration utilities  
- `[task_dao.py](/src/raztodo/infrastructure/sqlite/task_dao.py)` – Data access object for tasks  
- `[task_mapper.py](/src/raztodo/infrastructure/sqlite/task_mapper.py)` – Mapping between domain models and DB models  
- `[task_repository.py](/src/raztodo/infrastructure/sqlite/task_repository.py)` – SQLite implementation of TaskRepository  

---

### 4. Presentation Layer  
**Directory:** `presentation/cli/`

This layer manages user interaction. The project includes a simple command-line interface.

#### Key Files
- `[entrypoint.py](/src/raztodo/presentation/cli/entrypoint.py)` – CLI entry point  
- `[parser.py](/src/raztodo/presentation/cli/parser.py)` – Argument parsing  
- `[router.py](/src/raztodo/presentation/cli/router.py)` – Routes CLI commands to Use Cases  
- `[formatters.py](/src/raztodo/presentation/cli/formatters.py)` – Output formatting helpers  
- `[helpers.py](/src/raztodo/presentation/cli/helpers.py)` – Utility functions  

#### `commands/`
Command handlers for individual CLI operations:

- `[create_task_cmd.py](/src/raztodo/presentation/cli/commands/create_task_cmd.py)`  
- `[delete_task_cmd.py](/src/raztodo/presentation/cli/commands/delete_task_cmd.py)`  
- `[export_task_cmd.py](/src/raztodo/presentation/cli/commands/export_task_cmd.py)`  
- `[import_task_cmd.py](/src/raztodo/presentation/cli/commands/import_task_cmd.py)`  
- `[list_tasks_cmd.py](/src/raztodo/presentation/cli/commands/list_tasks_cmd.py)`  
- `[mark_task_done_cmd.py](/src/raztodo/presentation/cli/commands/mark_task_done_cmd.py)`  
- `[migrate_tasks_cmd.py](/src/raztodo/presentation/cli/commands/migrate_tasks_cmd.py)`  
- `[search_tasks_cmd.py](/src/raztodo/presentation/cli/commands/search_tasks_cmd.py)`  
- `[update_task_cmd.py](/src/raztodo/presentation/cli/commands/update_task_cmd.py)`  

---

### 5. Entry Point  
**File:** `__main__.py`

This project exposes its command-line interface (CLI) via a console script defined in `pyproject.toml`.
After installation, the CLI becomes available under the command:
```bash
raztodo
```

Example:
```bash
raztodo add "Task1" --desc "Test1"
```
You can list all commands:
```bash
raztodo --help
```
The `__main__.py` file remains part of the structure but is not intended for direct execution in typical usage.

