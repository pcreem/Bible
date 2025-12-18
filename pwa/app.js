let bible = null;
let currentBook = null;
let currentChapter = 1;
let autoScrollId = null;
let scrollVelocity = 0.5;

const contentEl = document.getElementById('content');
const bookSel = document.getElementById('book');
const chapterInput = document.getElementById('chapter');
const loadBtn = document.getElementById('load');
const startBtn = document.getElementById('start');
const stopBtn = document.getElementById('stop');
const scrollSpeed = document.getElementById('scrollSpeed');

async function loadBible() {
  try {
    const r = await fetch('../data/bible.json');
    bible = await r.json();
    const books = Object.keys(bible.books);
    bookSel.innerHTML = books.map(b => `<option value="${b}">${b}</option>`).join('');

    if (books.length > 0) {
      bookSel.value = books[0];
    }
  } catch (err) {
    console.error('Failed to load bible data:', err);
    contentEl.innerHTML = '<div style="text-align:center; color:#ef4444;">載入聖經資料失敗。</div>';
  }
}

/**
 * Renders the entire book and jumps to the specified chapter.
 */
function renderBook(bookName, chapterToJump) {
  if (!bible) return;

  const bookData = bible.books[bookName];
  if (!bookData) return;

  currentBook = bookName;
  const chapterKeys = Object.keys(bookData.chapters).sort((a, b) => parseInt(a) - parseInt(b));

  let html = `<div class="book-container">`;
  chapterKeys.forEach(chapNum => {
    const ch = bookData.chapters[chapNum];
    html += `<section id="chap-${chapNum}" class="chapter-section" data-chap="${chapNum}">`;
    html += `<h2 class="chapter-title" style="text-align:center; margin: 4rem 0 2rem; font-size:2.5rem; color:var(--primary);">${bookName} 第 ${chapNum} 章</h2>`;

    const verses = Object.keys(ch).sort((a, b) => parseInt(a) - parseInt(b));
    verses.forEach(v => {
      html += `<div class="verse-item"><span class="verse-num">${v}</span>${ch[v]}</div>`;
    });
    html += `</section>`;
  });

  // End of book marker
  html += `<div style="text-align:center; padding: 5rem 0; color: var(--text-muted); opacity: 0.5;">— ${bookName} 完結 —</div>`;
  html += `</div>`;

  contentEl.innerHTML = html;

  // Update book selector to match
  bookSel.value = bookName;

  // 關鍵修正：延後執行跳章，確保 DOM 已完全更新
  requestAnimationFrame(() => {
    contentEl.scrollTop = 0;  // 先強制回到頂端，避免舊位置殘留

    jumpToChapter(chapterToJump, false);  // 再跳到指定章節

    // 額外保險：如果跳轉失敗，再強制一次頂端
    setTimeout(() => {
      if (chapterToJump == 1 && contentEl.scrollTop > 100) {
        contentEl.scrollTop = 0;
      }
    }, 100);
  });

  // Save session
  localStorage.setItem('bible_session', JSON.stringify({ book: bookName, chapter: chapterToJump }));
}

function jumpToChapter(chapNum, smooth = true) {
  const target = document.getElementById(`chap-${chapNum}`);
  if (target) {
    // We update currentChapter so the UI matches
    currentChapter = parseInt(chapNum, 10);
    chapterInput.value = currentChapter;
    // Scroll the main content element
    contentEl.scrollTo({
      top: target.offsetTop - 20,
      behavior: smooth ? 'smooth' : 'auto'
    });
  }
}

function nextBook() {
  const books = Object.keys(bible.books);
  const currentIdx = books.indexOf(currentBook);
  if (currentIdx < books.length - 1) {
    const nextBookName = books[currentIdx + 1];
    renderBook(nextBookName, 1);

    // 額外保險：切換後立即歸零（某些瀏覽器仍可能殘留舊 scroll）
    contentEl.scrollTop = 0;

    return true;
  }
  return false;
}

function startAutoScroll() {
  stopAutoScroll();
  let last = performance.now();
  let nextBookPending = false;
  let currentPos = contentEl.scrollTop;
  let lastFrameTime = 0;

  function step(now) {
    if (!last) last = now;
    let dt = now - last;
    last = now;

    // Prevent huge jumps if tab was inactive or glitches
    if (dt > 100) dt = 16.67;

    const factor = parseFloat(scrollSpeed.value);
    scrollVelocity = 0.5 * factor;

    // Detect manual scroll and sync
    // Increased threshold to 20 to avoid conflict with browser scrollTop rounding/lag on mobile
    if (Math.abs(contentEl.scrollTop - currentPos) > 20) {
      currentPos = contentEl.scrollTop;
    }

    currentPos += scrollVelocity * (dt / 16.67);
    contentEl.scrollTop = currentPos;

    // Only update chapter info every ~200ms or when significant scroll happened to save CPU
    if (now - lastFrameTime > 200) {
      lastFrameTime = now;
      const sections = contentEl.querySelectorAll('.chapter-section');
      // Find the current chapter (check from bottom up to find the last one that passed the threshold)
      for (let i = sections.length - 1; i >= 0; i--) {
        const sec = sections[i];
        if (sec.offsetTop <= contentEl.scrollTop + 120) {
          const chap = sec.getAttribute('data-chap');
          if (currentChapter != chap) {
            currentChapter = chap;
            chapterInput.value = chap;
            localStorage.setItem('bible_session', JSON.stringify({ book: currentBook, chapter: chap }));
          }
          break; // Found the current chapter
        }
      }
    }

    // Check bottom for next book
    if (contentEl.scrollTop + contentEl.clientHeight >= contentEl.scrollHeight - 5) {
      if (!nextBookPending) {
        nextBookPending = true;
        setTimeout(() => {
          if (nextBook()) {
            last = performance.now();
            lastFrameTime = 0; // Force immediate chapter update check
            // 延遲同步 currentPos，確保 renderBook 的 requestAnimationFrame 已執行
            requestAnimationFrame(() => {
              currentPos = contentEl.scrollTop;
            });
            nextBookPending = false;
          } else {
            stopAutoScroll();
          }
        }, 2000);
      }
    }

    autoScrollId = requestAnimationFrame(step);
  }

  autoScrollId = requestAnimationFrame(step);
  startBtn.disabled = true;
  stopBtn.disabled = false;
}

function stopAutoScroll() {
  if (autoScrollId) cancelAnimationFrame(autoScrollId);
  autoScrollId = null;
  startBtn.disabled = false;
  stopBtn.disabled = true;
}

// Listeners
loadBtn.addEventListener('click', () => {
  stopAutoScroll();
  const book = bookSel.value;
  const chap = chapterInput.value || '1';

  // If we are already in the same book, just jump
  if (currentBook === book) {
    jumpToChapter(chap);
  } else {
    renderBook(book, chap);
  }
});

startBtn.addEventListener('click', () => startAutoScroll());
stopBtn.addEventListener('click', () => stopAutoScroll());

// Init
loadBible().then(() => {
  const saved = localStorage.getItem('bible_session');
  if (saved) {
    const { book, chapter } = JSON.parse(saved);
    bookSel.value = book;
    chapterInput.value = chapter;
    renderBook(book, chapter);
  } else {
    renderBook(bookSel.value, 1);
  }
});

window.addEventListener('keydown', (e) => {
  if (e.key === ' ') { e.preventDefault(); autoScrollId ? stopAutoScroll() : startAutoScroll(); }
  if (e.key === 'Escape') stopAutoScroll();
});

// Sync input if user manually scrolls
contentEl.addEventListener('scroll', () => {
  if (autoScrollId) return; // ignore if auto-scrolling
  const sections = contentEl.querySelectorAll('.chapter-section');
  for (let sec of sections) {
    if (sec.offsetTop <= contentEl.scrollTop + 100) {
      const chap = sec.getAttribute('data-chap');
      if (currentChapter != chap) {
        currentChapter = chap;
        chapterInput.value = chap;
      }
    }
  }
});
