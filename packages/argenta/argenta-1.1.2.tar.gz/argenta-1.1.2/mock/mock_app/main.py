from mock.mock_app.routers import work_router

from argenta import App, Orchestrator
from argenta.app import PredefinedMessages, DynamicDividingLine, AutoCompleter
from argenta.orchestrator import ArgParser
from argenta.orchestrator.argparser import BooleanArgument, ValueArgument
from dishka import Provider, provide, Scope  # type: ignore


class temProvider(Provider):
    @provide(scope=Scope.APP)
    def get_apace(self) -> int:
        return 1234

arg_parser: ArgParser = ArgParser(
    processed_args=[
        BooleanArgument(name="repeat", is_deprecated=True),
        ValueArgument(name="required", is_required=True),
    ]
)
app: App = App(
    dividing_line=DynamicDividingLine(),
    autocompleter=AutoCompleter(),
)
orchestrator: Orchestrator = Orchestrator(arg_parser, custom_providers=[temProvider()])


def main():
    app.include_router(work_router)

    app.add_message_on_startup(PredefinedMessages.USAGE)
    app.add_message_on_startup(PredefinedMessages.AUTOCOMPLETE)
    app.add_message_on_startup(PredefinedMessages.HELP)

    orchestrator.start_polling(app)


if __name__ == "__main__":
    main()
