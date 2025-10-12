# TODO: API_REFERENCE.md Updates

**Status**: Needs updating to remove `exclude` parameter references
**Priority**: Medium
**Estimated effort**: 15-20 minutes

## Background

After the include-only workflow refactor, the `exclude` parameter was removed from:
- `BreadcrumbConfig` dataclass
- `breadcrumb.init()` function
- All CLI commands

## Required Changes in API_REFERENCE.md

### 1. Line 43: Function signature
**Current**:
```python
def init(
    enabled: Optional[bool] = None,
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,  # REMOVE THIS
    ...
)
```

**Update to**:
```python
def init(
    enabled: Optional[bool] = None,
    include: Optional[List[str]] = None,
    sample_rate: Optional[float] = None,
    ...
)
```

### 2. Line 55: Parameter description
**Current**: Has `exclude` parameter description

**Action**: Remove the entire `exclude` parameter description

### 3. Line 101: Example code
**Current**:
```python
breadcrumb.init(
    include=["src/**/*.py"],
    exclude=["tests/**", "scripts/**"]
)
```

**Update to**:
```python
breadcrumb.init(
    include=["src/**/*.py"],
)
```

### 4. Line 230: BreadcrumbConfig attributes
**Current**: Lists `exclude` in attributes

**Action**: Remove `exclude` from attribute list

### 5. Line 246: Example code
**Current**:
```python
config = BreadcrumbConfig(
    enabled=True,
    include=["src/**/*.py"],
    exclude=["tests/**"],
    ...
)
```

**Update to**:
```python
config = BreadcrumbConfig(
    enabled=True,
    include=["src/**/*.py"],
    sample_rate=0.5,
    ...
)
```

## How to Complete

```bash
# 1. Read the file
# 2. Search for all "exclude" references
# 3. Remove exclude parameters from signatures
# 4. Remove exclude from examples
# 5. Update docstrings
# 6. Verify no broken examples remain
```

## Validation

After updates:
- [ ] No references to `exclude` parameter
- [ ] All code examples are valid
- [ ] API signatures match actual implementation in config.py
- [ ] Include-only workflow is clear in examples

---

*Created during documentation cleanup - January 2025*
