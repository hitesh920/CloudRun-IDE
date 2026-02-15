import { useRef, useEffect } from 'react'
import Editor from '@monaco-editor/react'

// Language configuration map
export const LANGUAGE_CONFIGS = {
  python: {
    monacoLanguage: 'python',
    template: `# Python Code
print("Hello, World!")
`,
  },
  nodejs: {
    monacoLanguage: 'javascript',
    template: `// Node.js Code
console.log("Hello, World!");
`,
  },
  java: {
    monacoLanguage: 'java',
    template: `public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
`,
  },
  cpp: {
    monacoLanguage: 'cpp',
    template: `#include <iostream>
using namespace std;

int main() {
    cout << "Hello, World!" << endl;
    return 0;
}
`,
  },
  html: {
    monacoLanguage: 'html',
    template: `<!DOCTYPE html>
<html>
<head>
    <title>Page</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
        h1 { color: #333; }
    </style>
</head>
<body>
    <h1>Hello, World!</h1>
    <p>Edit this HTML and click Run to preview.</p>
</body>
</html>
`,
  },
  ubuntu: {
    monacoLanguage: 'shell',
    template: `# Ubuntu Shell
echo "Hello, World!"
`,
  },
}

export function CodeEditor({ language, code, onChange, theme = 'vs-dark' }) {
  const editorRef = useRef(null)

  const handleEditorDidMount = (editor) => {
    editorRef.current = editor
    editor.focus()
  }

  // Update editor value when code changes externally (e.g., AI fix)
  useEffect(() => {
    if (editorRef.current) {
      const currentValue = editorRef.current.getValue()
      if (currentValue !== code) {
        editorRef.current.setValue(code)
      }
    }
  }, [code])

  const config = LANGUAGE_CONFIGS[language] || LANGUAGE_CONFIGS.python

  return (
    <Editor
      height="100%"
      language={config.monacoLanguage}
      value={code}
      theme={theme}
      onChange={(value) => onChange(value || '')}
      onMount={handleEditorDidMount}
      options={{
        fontSize: 14,
        fontFamily: "'Cascadia Code', 'Fira Code', Consolas, 'Courier New', monospace",
        minimap: { enabled: false },
        scrollBeyondLastLine: false,
        automaticLayout: true,
        tabSize: language === 'python' ? 4 : 2,
        wordWrap: language === 'html' ? 'on' : 'off',
        lineNumbers: 'on',
        renderWhitespace: 'selection',
        bracketPairColorization: { enabled: true },
        guides: { bracketPairs: true },
        padding: { top: 8 },
        cursorBlinking: 'smooth',
        smoothScrolling: true,
        contextmenu: true,
        folding: true,
        suggest: {
          showKeywords: true,
          showSnippets: true,
        },
      }}
    />
  )
}

export default CodeEditor
