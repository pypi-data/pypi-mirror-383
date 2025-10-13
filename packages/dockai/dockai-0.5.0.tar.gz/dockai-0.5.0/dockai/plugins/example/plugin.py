class ExamplePlugin:
    name = "example"
    version = "0.1.0"

    def on_start(self, ctx):
        print(f"[hello] on_start: {ctx.get('container_name')}")

    def on_logs_fetched(self, ctx, logs):
        print(f"[hello] logs fetched: {len(logs or '')} chars")

    def on_ai_response(self, ctx, response, meta):
        print(f"[hello] ai_response: {len(response or '')} chars")

    def on_finish(self, ctx, result):
        print(f"[hello] finish: keys={list((result or {}).keys())}")

plugin = ExamplePlugin()