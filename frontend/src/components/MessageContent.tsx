import React from 'react';

function renderInline(text: string, keyPrefix: string): React.ReactNode[] {
  const parts = text.split(/(\*\*[^*]+\*\*|`[^`]+`|\*[^*]+\*)/g).filter(Boolean);
  return parts.map((part, index) => {
    const key = `${keyPrefix}-${index}`;
    if (part.startsWith('**') && part.endsWith('**')) return <strong key={key}>{part.slice(2, -2)}</strong>;
    if (part.startsWith('`') && part.endsWith('`')) return <code key={key}>{part.slice(1, -1)}</code>;
    if (part.startsWith('*') && part.endsWith('*')) return <em key={key}>{part.slice(1, -1)}</em>;
    return <React.Fragment key={key}>{part}</React.Fragment>;
  });
}

export const MessageContent: React.FC<{ content: string }> = ({ content }) => {
  const lines = content.replace(/\r\n?/g, '\n').split('\n');
  const blocks: React.ReactNode[] = [];
  let paragraph: string[] = [];
  let list: string[] = [];
  let listType: 'ul' | 'ol' | null = null;
  let code: string[] | null = null;
  let codeLanguage = '';

  const flushParagraph = () => {
    if (!paragraph.length) return;
    blocks.push(<p key={`p-${blocks.length}`}>{renderInline(paragraph.join(' '), `p-${blocks.length}`)}</p>);
    paragraph = [];
  };
  const flushList = () => {
    if (!list.length || !listType) return;
    const items = list.map((item, index) => <li key={index}>{renderInline(item, `li-${blocks.length}-${index}`)}</li>);
    blocks.push(listType === 'ol' ? <ol key={`ol-${blocks.length}`}>{items}</ol> : <ul key={`ul-${blocks.length}`}>{items}</ul>);
    list = [];
    listType = null;
  };

  lines.forEach((line, index) => {
    const fence = line.match(/^\s*```\s*([\w+-]*)\s*$/);
    if (fence) {
      flushParagraph();
      flushList();
      if (code) {
        blocks.push(<pre key={`code-${blocks.length}`} data-language={codeLanguage || undefined}><code>{code.join('\n')}</code></pre>);
        code = null;
        codeLanguage = '';
      } else {
        code = [];
        codeLanguage = fence[1];
      }
      return;
    }
    if (code) {
      code.push(line);
      return;
    }

    const heading = line.match(/^\s*(#{1,3})\s+(.+)$/);
    if (heading) {
      flushParagraph();
      flushList();
      const level = heading[1].length;
      const content = renderInline(heading[2], `h-${index}`);
      blocks.push(level === 1 ? <h2 key={`h-${index}`}>{content}</h2> : level === 2 ? <h3 key={`h-${index}`}>{content}</h3> : <h4 key={`h-${index}`}>{content}</h4>);
      return;
    }

    const bullet = line.match(/^\s*[-*]\s+(.+)$/);
    const numbered = line.match(/^\s*\d+[.)]\s+(.+)$/);
    if (bullet || numbered) {
      flushParagraph();
      const nextType = numbered ? 'ol' : 'ul';
      if (listType && listType !== nextType) flushList();
      listType = nextType;
      list.push((bullet || numbered)![1]);
      return;
    }
    if (!line.trim()) {
      flushParagraph();
      flushList();
      return;
    }
    flushList();
    paragraph.push(line.trim());
  });

  const trailingCode = code as string[] | null;
  if (trailingCode) blocks.push(<pre key={`code-${blocks.length}`} data-language={codeLanguage || undefined}><code>{trailingCode.join('\n')}</code></pre>);
  flushParagraph();
  flushList();
  return <div className="message-content">{blocks}</div>;
};
