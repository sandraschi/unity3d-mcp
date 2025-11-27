# Performance Optimization Expert

Analyze and optimize the current Unity project or asset.

## Target
- **Asset/Scene**: {{target_path}}
- **Platform**: {{platform}}
- **Performance Goal**: {{performance_goal}} (e.g., 60fps on Quest 2, VRChat Good Rank)

## Optimization Steps
1.  Analyze textures: Check resolution, compression, and mipmaps.
2.  Analyze meshes: Check polygon count and topology.
3.  Analyze materials: Check shader complexity and draw calls.
4.  Apply automated optimizations using `optimize_textures` or `optimize_for_platform`.
5.  Generate a report of changes made.
