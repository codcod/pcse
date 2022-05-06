.PHONY = venv mypy check test

export PYTHONPATH=.

src=pcse

venv:
	python -m venv .venv
	( bash -c "source .venv/bin/activate && python -m pip install --upgrade pip setuptools wheel"; )
	( bash -c "source .venv/bin/activate && pip install -r requirements.txt"; )
	@printf "\nDone. You can now activate the virtual environment:\n  source .venv/bin/activate\n"

mypy:
	mypy --strict --scripts-are-modules --implicit-reexport pcse
		#scripts/*

check:
	@printf "\n-[ pylint ]-\n"
	@pylint $(src); \
    case "$$?" in \
		20) printf "*** ERR: suppressing errors and moving on \n";; \
    esac;
	@printf "\n-[ flake8 ]-\n"
	@flake8 $(src); \
    case "$$?" in \
		1) printf "*** ERR: suppressing errors and moving on \n";; \
    esac;
	@printf "\n-[ pydocstyle ]-\n"
	@pydocstyle $(src); \
    case "$$?" in \
		20) printf "*** ERR: suppressing errors and moving on \n";; \
    esac;

test:
	pytest  # configured via pyproject.toml
