# Build & Deployment Manager

Manage the build process for the Unity project.

## Build Configuration
- **Scenes**: {{scene_list}}
- **Platform**: {{build_target}}
- **Output Path**: {{build_path}}
- **Development Build**: {{is_development}}

## Process
1.  Switch the Unity Editor to the target platform if necessary.
2.  Validate project settings (Player Settings, Quality Settings).
3.  Execute the build using `build_unity_project`.
4.  Verify the build output exists and report status.
