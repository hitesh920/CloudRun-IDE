import { useState, useRef } from 'react'
import Editor from '@monaco-editor/react'

const LANGUAGE_CONFIGS = {
  python: { 
    monaco: 'python',
    template: `# Python Code
print("Hello, World!")
`
  },
  nodejs: { 
    monaco: 'javascript',
    template: `// Node.js Code
console.log("Hello, World!");
`
  },
  java: { 
    monaco: 'java',
    template: `public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
`
  },
  cpp: { 
    monaco: 'cpp',
    template: `#include <iostream>
using namespace std;

int main() {
    cout << "Hello, World!" << endl;
    return 0;
}
`
  },
  html: { 
    monaco: 'html',
    template: `<!DOCTYPE html>
<html>
<head>
    <title>Page</title>
</head>
<body>
    <h1>Hello, World!</h1>
</body>
</html>
`
  },
}

function CodeEditor({ language, code, onChange, theme = 'vs-dark' }) {
  const editorRef = useRef(null)
  const languageConfig = LANGUAGE_CONFIGS[language] || LANGUAGE_CONFIGS.python

  const handleEditorDidMount = (editor, monaco) => {
    editorRef.current = editor
    
    // Configure editor options
    editor.updateOptions({
      fontSize: 14,
      minimap: { enabled: true },
      scrollBeyondLastLine: false,
      wordWrap: 'on',
      automaticLayout: true,
    })
  }

  const handleEditorChange = (value) => {
    if (onChange) {
      onChange(value || '')
    }
  }

  return (
    <Editor
      height="100%"
      language={languageConfig.monaco}
      value={code}
      theme={theme}
      onChange={handleEditorChange}
      onMount={handleEditorDidMount}
      options={{
        selectOnLineNumbers: true,
        roundedSelection: false,
        readOnly: false,
        cursorStyle: 'line',
        automaticLayout: true,
        fontSize: 14,
        fontFamily: 'Monaco, Consolas, "Courier New", monospace',
        lineNumbers: 'on',
        tabSize: 4,
        insertSpaces: true,
        scrollBeyondLastLine: false,
        wordWrap: 'on',
        minimap: {
          enabled: true,
        },
      }}
      loading={
        <div className="h-full flex items-center justify-center bg-gray-900">
          <div className="text-gray-400">Loading editor...</div>
        </div>
      }
    />
  )
}

export { CodeEditor, LANGUAGE_CONFIGS }
