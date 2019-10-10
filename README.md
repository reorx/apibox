# APIBox

**Note**: This project is deprecated and will not be maintained in the future.
The reason is that, `apibox.object` is a snippet rather than a library,
it should be copied and modified in the place where a base class is needed for writing RPC or HTTP Client code.

And `apibox.testing` is too simple, [HttpRunner](https://github.com/HttpRunner/HttpRunner) does the same thing
much better, though what I wrote is more suitable for small use cases, but I really don't want too much
"YAML/JSON based DSL for HTTP API calls" appear in this world, so just let it retire :)

---

API tools all in one, for dedicated web developers

## TODO

- [ ] specify json schema for check input parameters & output data
- [ ] specify python/js code for assertion
- [ ] support ansible playbook style module using, for both request and response lifecycle handling
