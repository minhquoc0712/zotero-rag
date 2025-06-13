# Release Guide for Zotero RAG Executables

This guide explains how to build and distribute standalone executables for Windows, Linux, and macOS.

## Quick Start

### Local Testing (Before CI/CD)

1. **Test build locally**:
   ```bash
   python build_executable.py
   ```

2. **Test the executable**:
   ```bash
   # Linux/macOS
   ./dist/zotero-rag --help

   # Windows
   ./dist/zotero-rag.exe --help
   ```

### Automated CI/CD Pipeline

1. **Push code to trigger builds**:
   ```bash
   git add .
   git commit -m "Update for release"
   git push origin main
   ```

2. **Create a release for distribution**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
   Or create a release through GitHub's web interface.

## Distribution Process

### Automatic Builds

The GitHub Actions workflow automatically:

- ✅ Builds executables for Windows, Linux, and macOS
- ✅ Tests each executable with `--help` command
- ✅ Uploads artifacts for every push/PR
- ✅ Attaches binaries to GitHub releases
- ✅ Packages with LICENSE and README

### Build Artifacts

After a successful build, you'll get:

- `zotero-rag-windows.zip` - Windows executable + docs
- `zotero-rag-linux.tar.gz` - Linux executable + docs  
- `zotero-rag-macos.tar.gz` - macOS executable + docs

### File Sizes

Expect executable sizes around:
- **Windows**: ~150-300 MB
- **Linux**: ~120-250 MB  
- **macOS**: ~130-280 MB

*Note: Large size due to ML models (sentence-transformers, faiss, etc.)*

## Installation Instructions for Users

### Windows
1. Download `zotero-rag-windows.zip`
2. Extract the zip file
3. Run `zotero-rag.exe` from command prompt or PowerShell

### Linux
1. Download `zotero-rag-linux.tar.gz`
2. Extract: `tar -xzf zotero-rag-linux.tar.gz`
3. Make executable: `chmod +x zotero-rag`
4. Run: `./zotero-rag`

### macOS
1. Download `zotero-rag-macos.tar.gz`
2. Extract: `tar -xzf zotero-rag-macos.tar.gz`
3. Make executable: `chmod +x zotero-rag`
4. Run: `./zotero-rag`

*Note: On macOS, you may need to allow the app in Security & Privacy settings*

## Release Checklist

### Before Release
- [ ] Test local build with `python build_executable.py`
- [ ] Verify all features work in executable
- [ ] Update version in `__init__.py`
- [ ] Update CHANGELOG.md
- [ ] Update README.md if needed

### Creating Release
- [ ] Push all changes to main branch
- [ ] Wait for CI/CD to pass
- [ ] Create GitHub release with tag (e.g., v1.0.0)
- [ ] Add release notes describing changes
- [ ] Verify all three platform binaries are attached

### After Release
- [ ] Test download and installation on each platform
- [ ] Update documentation with download links
- [ ] Announce release (if applicable)

## Troubleshooting

### Common Build Issues

1. **Missing dependencies**:
   ```bash
   pip install pyinstaller sentence-transformers faiss-cpu PyPDF2 scikit-learn
   ```

2. **Import errors in executable**:
   - Check `hiddenimports` in `zotero-rag.spec`
   - Add missing modules to the spec file

3. **Large executable size**:
   - This is expected due to ML dependencies
   - Consider UPX compression (already enabled)

4. **Runtime errors**:
   - Test locally first with `python build_executable.py`
   - Check for missing data files in spec

### Platform-Specific Issues

**Windows:**
- Antivirus may flag the executable (false positive)
- May need to run as administrator for first use

**macOS:**
- Users need to allow unsigned applications
- May require: `xattr -d com.apple.quarantine zotero-rag`

**Linux:**
- Ensure executable permissions: `chmod +x zotero-rag`
- May need additional system libraries on some distributions

## Advanced Configuration

### Customizing the Build

Edit `zotero-rag.spec` to:
- Add/remove dependencies
- Include additional data files
- Exclude unnecessary modules
- Configure build options

### Adding Code Signing

For production releases, consider:
- Windows: Authenticode signing
- macOS: Developer ID signing
- Linux: GPG signing

### Creating Installers

For better user experience:
- Windows: Use NSIS or WiX to create MSI installers
- macOS: Create DMG files with background images
- Linux: Build DEB/RPM packages

## Support

For build issues:
1. Check the GitHub Actions logs
2. Test locally with the build script
3. Review PyInstaller documentation
4. Open an issue with build logs 