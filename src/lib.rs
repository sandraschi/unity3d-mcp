use zed_extension_api as zed;

struct Unity3DGameDevelopmentExtension;

impl zed::Extension for Unity3DGameDevelopmentExtension {
    fn context_server_command(
        &mut self,
        id: &zed::ContextServerId,
        _project: &zed::Project,
    ) -> zed::Result<zed::Command> {
        match id.0.as_str() {
            "unity3d-mcp" => Ok(zed::Command {
                command: "uv".to_string(),
                args: vec!["run".to_string(), "unity3d-mcp".to_string()],
                env: Default::default(),
            }),
            _ => Err(format!("Unknown server: {}", id.0)),
        }
    }
}

zed::register_extension!(Unity3DGameDevelopmentExtension);
