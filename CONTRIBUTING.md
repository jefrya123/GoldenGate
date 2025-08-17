# Contributing to GoldenGate PII Scanner

## 🚀 Git Workflow

**IMPORTANT**: Main branch is now protected for stable releases only.

### Branch Strategy

- **`main`** - Production releases only (protected)
- **`develop`** - Active development branch
- **`feature/*`** - New features
- **`hotfix/*`** - Critical bug fixes
- **`release/*`** - Release preparation

### Development Workflow

1. **For new features**:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   # ... make changes ...
   git push origin feature/your-feature-name
   # Create PR to develop branch
   ```

2. **For bug fixes**:
   ```bash
   git checkout develop
   git pull origin develop  
   git checkout -b bugfix/fix-description
   # ... make changes ...
   git push origin bugfix/fix-description
   # Create PR to develop branch
   ```

3. **For critical hotfixes**:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b hotfix/critical-fix
   # ... make changes ...
   git push origin hotfix/critical-fix
   # Create PR to main AND develop
   ```

### Release Process

1. **Prepare release from develop**:
   ```bash
   git checkout develop
   git checkout -b release/v1.1.0
   # Update version numbers, docs
   git push origin release/v1.1.0
   ```

2. **Merge to main and tag**:
   ```bash
   git checkout main
   git merge release/v1.1.0
   git tag -a v1.1.0 -m "Release v1.1.0"
   git push origin main --tags
   ```

3. **Merge back to develop**:
   ```bash
   git checkout develop
   git merge main
   git push origin develop
   ```

## 🔒 Branch Protection

- **Main branch**: Requires PR approval, no direct pushes
- **Develop branch**: Active development, requires PR review
- **Tag releases**: Use semantic versioning (v1.0.0, v1.1.0, etc.)

## 📋 Pull Request Guidelines

1. **Clear title** describing the change
2. **Detailed description** with context and reasoning
3. **Link to issues** if applicable
4. **Test coverage** for new features
5. **Documentation updates** if needed

## 🧪 Testing Requirements

- All new features must include tests
- Run full test suite: `python demo_test.py`
- Performance testing for large file features
- Security review for PII handling changes

## 📚 Documentation

- Update README.md for major changes
- Update QUICK_START.md for usage changes  
- Add inline code documentation
- Update STATUS.md for significant improvements

## 🔐 Security Guidelines

- Never commit test files with real PII
- Use synthetic test data only
- Review all PII handling code carefully
- Follow defensive coding practices

## 📦 Release Checklist

- [ ] All tests passing
- [ ] Documentation updated
- [ ] Version numbers updated
- [ ] Security review completed
- [ ] Performance testing on large files
- [ ] Clean git history
- [ ] Tag created with release notes

## 🎯 Current Status

**v1.0.0 - PRODUCTION READY** 
- ✅ Smart classification (no hardcoding)
- ✅ Large file optimization
- ✅ User-friendly interfaces
- ✅ VM deployment ready

**Next milestone: v1.1.0**
- Performance improvements based on user testing
- Additional file format support
- Enhanced monitoring and reporting