# 📚 Unity3D-MCP Documentation Portal

The Unity3D-MCP (SOTA 2026) documentation suite provides a comprehensive guide to automating one of the world's most powerful game engines for both virtual and physical robotics.

---

## 🎯 **Quick Navigation**

### **Core Concepts**
- 🏗️ **[Architecture: Dual-Mode](ARCHITECTURE_DUAL_MODE.md)**: Deep dive into "Hands-In" (Live) and "Hands-Off" (Disk) operations.
- 📘 **[Complete API Reference](API_REFERENCE.md)**: Comprehensive dictionary for all 50+ tools.

### **Specialized Guides**
- 🎭 **[VRM-to-VRChat Pipeline](GUIDE_VRCHAT_PIPELINE.md)**: Optimization, rigging, and upload automation for avatars.
- 🕹️ **[Real-Time Editor Automation](GUIDE_EDITOR_AUTO.md)**: Scene manipulation through the MCP Bridge script.

### **Environment Setup**
- 🛠️ **Installation Guide**: Located in [README.md](../README.md).
- 🔑 **The Bridge**: [MCPBridge.cs](../src/unity3d_mcp/resources/MCPBridge.cs) - The heart of live automation.

---

## 🚀 **Industrial-Grade Workflows**

### **Level Design Automation**
Use the **Hands-In** bridge to layout objects, set lighting, and manage hierarchy. Ideal for dynamic world generation and rapid prototyping.

### **CI/CD Build Pipelines**
Use the **Hands-Off** UnityPy tools to audit asset polycounts and texture memory before triggering a multi-platform build via the server's build tools.

### **Robotics Integration**
The `robotics-mcp` (Composite) uses this server as a core dependency for high-fidelity visualization in Unity and VRChat.

---

## 📊 **Documentation Status**

| Category | Status | Last Updated |
|----------|--------|--------------|
| Architecture | ✅ SOTA | 2026-04-02 |
| API Docs | ✅ SOTA | 2026-04-02 |
| VRM Pipeline | ✅ SOTA | 2026-04-02 |
| Editor Bridge | ✅ SOTA | 2026-04-02 |
| Packaging | ✅ mcpb ready | 2026-04-02 |

---

*Unity3D-MCP Technical Suite*  
*Created: April 2, 2026*  
*Location: `docs/README.md`*  
*Status: Complete and 0% Notepadpp Contamination* 🛡️
