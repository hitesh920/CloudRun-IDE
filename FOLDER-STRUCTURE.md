# CloudRun IDE - Folder Structure Guide

## 📁 Step-by-Step Folder Creation

### Step 1: Create Root Structure
```
cloudrun-ide/
├── backend/
├── frontend/
├── deployment/
└── docs/
```

### Step 2: Backend Folders
```
backend/
├── app/
│   ├── core/
│   ├── services/
│   ├── api/
│   └── utils/
├── dockerfiles/
└── scripts/
```

### Step 3: Frontend Folders
```
frontend/
├── public/
└── src/
    ├── components/
    ├── services/
    ├── hooks/
    ├── utils/
    └── styles/
```

## 🔧 Terminal Commands

```bash
# Create all folders at once
mkdir -p cloudrun-ide/{backend/{app/{core,services,api,utils},dockerfiles,scripts},frontend/{public,src/{components,services,hooks,utils,styles}},deployment,docs}
```

Or step by step:

```bash
# Navigate to project root
cd cloudrun-ide

# Backend
mkdir -p backend/app/{core,services,api,utils}
mkdir -p backend/{dockerfiles,scripts}

# Frontend
mkdir -p frontend/public
mkdir -p frontend/src/{components,services,hooks,utils,styles}

# Other
mkdir -p deployment docs
```
