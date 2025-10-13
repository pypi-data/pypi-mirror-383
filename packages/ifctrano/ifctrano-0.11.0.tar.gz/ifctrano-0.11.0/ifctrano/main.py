import shutil
import webbrowser
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Annotated, get_args, Callable

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn
from trano.data_models.conversion import convert_network  # type: ignore
from trano.elements.library.library import Library  # type: ignore
from trano.reporting.html import to_html_reporting  # type: ignore
from trano.reporting.reporting import ModelDocumentation  # type: ignore
from trano.reporting.types import ResultFile  # type: ignore
from trano.simulate.simulate import simulate  # type: ignore
from trano.topology import Network  # type: ignore
from trano.utils.utils import is_success  # type: ignore

from ifctrano.base import Libraries
from ifctrano.building import Building
from ifctrano.exceptions import InvalidLibraryError
from rich import print

app = typer.Typer()
CHECKMARK = "[green]✔[/green]"
CROSS_MARK = "[red]✘[/red]"


def _create_network(model: str, library: str) -> Network:
    library_ = Library.from_configuration(library)
    model_ = Path(model).resolve()
    return convert_network(str(model_.stem), model_, library=library_)


def _simulate(
    modelica_model_path: Path, create_network_callable: Callable[[], Network]
) -> None:
    print("Simulating...")
    try:
        results = simulate(modelica_model_path.parent, create_network_callable())
    except Exception as e:
        print(f"{CROSS_MARK} Simulation failed: {e}")
        return
    if not is_success(results):
        print(f"{CROSS_MARK} Simulation failed. See logs for more information.")
        return

    result_path = (
        Path(modelica_model_path.parent)
        / "results"
        / f"{modelica_model_path.stem.lower()}.building_res.mat"
    )
    if not result_path.exists():
        print(
            f"{CROSS_MARK} Simulation failed. Result file not found in {result_path}."
        )
        return
    reporting = ModelDocumentation.from_network(
        create_network_callable(),
        result=ResultFile(path=result_path),
    )
    html = to_html_reporting(reporting)
    report_path = Path(modelica_model_path.parent / f"{modelica_model_path.stem}.html")
    report_path.write_text(html)
    webbrowser.open(f"file://{report_path}")


@app.command()
def config(
    model: Annotated[
        str,
        typer.Argument(help="Local path to the ifc file."),
    ],
    show_space_boundaries: Annotated[
        bool,
        typer.Option(help="Show computed space boundaries."),
    ] = False,
) -> None:
    working_directory = Path.cwd()
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        modelica_model_path = Path(model).resolve().with_suffix(".mo")
        config_path = working_directory.joinpath(f"{modelica_model_path.stem}.yaml")
        task = progress.add_task(
            description=f"Generating {config_path} configuration file.",
            total=None,
        )
        building = Building.from_ifc(Path(model))
        if show_space_boundaries:
            print(f"{CHECKMARK} Showing space boundaries.")
            building.show()
        building.to_yaml(config_path)
        progress.remove_task(task)
        print(f"{CHECKMARK} configuration file generated: {config_path}.")


@app.command()
def from_config(
    model: Annotated[
        str,
        typer.Argument(help="Path to the configuration yaml file."),
    ],
    library: Annotated[
        str,
        typer.Argument(help="Modelica library to be used for simulation."),
    ] = "Buildings",
    simulate_model: Annotated[
        bool,
        typer.Option(help="Simulate the generated model."),
    ] = False,
) -> None:
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        modelica_model_path = Path(model).resolve().with_suffix(".mo")
        task = progress.add_task(
            description=f"Generating model {modelica_model_path.name} with library {library}",
            total=None,
        )
        network = _create_network(model, library)
        modelica_model = network.model()
        progress.update(task, completed=True)
        task = progress.add_task(description="Writing model to file...", total=None)
        modelica_model_path.write_text(modelica_model)
        progress.remove_task(task)
        print(f"{CHECKMARK} Model generated at {modelica_model_path}")
        create_network_callable = lambda: _create_network(model, library)  # noqa: E731
        if simulate_model:
            _simulate(modelica_model_path, create_network_callable)


@app.command()
def create(
    model: Annotated[
        str,
        typer.Argument(help="Local path to the ifc file."),
    ],
    library: Annotated[
        str,
        typer.Argument(help="Modelica library to be used for simulation."),
    ] = "Buildings",
    show_space_boundaries: Annotated[
        bool,
        typer.Option(help="Show computed space boundaries."),
    ] = False,
    simulate_model: Annotated[
        bool,
        typer.Option(help="Simulate the generated model."),
    ] = False,
) -> None:
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        if library not in get_args(Libraries):
            raise InvalidLibraryError(
                f"Invalid library {library}. Valid libraries are {get_args(Libraries)}"
            )
        modelica_model_path = Path(model).resolve().with_suffix(".mo")
        task = progress.add_task(
            description=f"Generating model {modelica_model_path.name} with library {library} from {model}",
            total=None,
        )
        building = Building.from_ifc(Path(model))
        if show_space_boundaries:
            print(f"{CHECKMARK} Showing space boundaries.")
            building.show()
        modelica_network = building.create_network(library=library)  # type: ignore
        progress.update(task, completed=True)
        task = progress.add_task(description="Writing model to file...", total=None)
        modelica_model_path.write_text(modelica_network.model())
        progress.remove_task(task)
        print(f"{CHECKMARK} Model generated at {modelica_model_path}")
        create_network_callable = lambda: building.create_network(  # noqa: E731
            library=library  # type: ignore
        )
        if simulate_model:
            _simulate(modelica_model_path, create_network_callable)


@app.command()
def verify() -> None:
    verification_ifc = Path(__file__).parent / "example" / "verification.ifc"
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress, TemporaryDirectory() as temp_dir:
        temp_ifc_file = Path(temp_dir) / verification_ifc.name
        shutil.copy(verification_ifc, temp_ifc_file)
        task = progress.add_task(
            description="Trying to create a model from a test file...",
            total=None,
        )
        building = Building.from_ifc(temp_ifc_file)
        building.save_model()
        if temp_ifc_file.parent.joinpath(f"{building.name}.mo").exists():
            progress.remove_task(task)
            print(f"{CHECKMARK} Model successfully created... your system is ready.")
        else:
            progress.remove_task(task)
            print(
                f"{CROSS_MARK} Model could not be created... please check your system."
            )


if __name__ == "__main__":
    app()
