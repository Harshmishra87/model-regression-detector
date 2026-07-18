from jinja2 import Environment, FileSystemLoader


def generate_report(
    diff: dict,
    run_meta: dict,
    history: list[float],
    regressed_cases: list[dict],
    output_path: str = "results/report.html",
) -> str:
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("report.html")

    html = template.render(
        prompt_version=run_meta["prompt_version"],
        model=run_meta["model"],
        timestamp=run_meta["timestamp"],
        current_pass_rate=diff["current_pass_rate"],
        previous_pass_rate=diff["previous_pass_rate"],
        delta=diff["pass_rate_delta"],
        regressed_cases=regressed_cases,
        history=history,
    )

    with open(output_path, "w") as f:
        f.write(html)

    return output_path