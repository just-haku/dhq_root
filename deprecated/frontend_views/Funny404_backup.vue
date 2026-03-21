<template>
  <div class="elegant-404-container">
    <!-- Animated Background -->
    <div class="bg-animation">
      <div class="gradient-orb orb-1"></div>
      <div class="gradient-orb orb-2"></div>
      <div class="gradient-orb orb-3"></div>
      <div class="grid-pattern">
        <div v-for="i in 50" :key="i" class="grid-dot" :style="getGridDotStyle(i)"></div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="content-container">
      <!-- 404 Animation -->
      <div class="error-animation">
        <div class="error-number">
          <span class="digit digit-4">4</span>
          <span class="digit digit-0">0</span>
          <span class="digit digit-4">4</span>
        </div>
        <div class="error-glow"></div>
      </div>

      <!-- Message -->
      <div class="error-message">
        <h1 class="error-title">Page Not Found</h1>
        <p class="error-description">{{ currentReason.message }}</p>
        <p class="error-subtitle">{{ currentReason.excuse }}</p>
      </div>

      <!-- Actions -->
      <div class="action-container">
        <button @click="goHome" class="action-btn primary-btn">
          <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
            <polyline points="9 22 9 12 15 12 15 22"></polyline>
          </svg>
          Go Home
        </button>
        <button @click="refreshPage" class="action-btn secondary-btn">
          <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="23 4 23 10 17 10"></polyline>
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
          </svg>
          Refresh
        </button>
      </div>

      <!-- Subtle Easter Egg -->
      <div class="easter-egg">
        <p class="subtle-text">The journey is the destination</p>
        <!-- Hidden Game Link (1 in 20 chance) -->
        <div v-if="showGameLink" class="game-link-container">
          <p class="game-hint">🎮 Feeling lost? Try a different adventure...</p>
          <button @click="openGame" class="game-btn">
            <svg class="game-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="2" y="6" width="20" height="12" rx="2"></rect>
              <path d="M6 12h4m0 0v4m0-4l-4 4m6-4v4m0-4l4 4"></path>
            </svg>
            Play Mini Game
          </button>
        </div>
      </div>
    </div>

    <!-- Floating Elements -->
    <div class="floating-elements">
      <div v-for="i in 8" :key="i" class="float-element" :style="getFloatStyle(i)">
        <div class="float-shape"></div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Elegant404',
  data() {
    return {
      currentReasonIndex: 0,
      showGameLink: false,
      reasons: [
        {
          message: "The page you're looking for doesn't exist",
          excuse: "It may have been moved, deleted, or never existed in the first place."
        },
        {
          message: "We couldn't find the page you requested",
          excuse: "Please check the URL and try again, or return to the homepage."
        },
        {
          message: "This page seems to have vanished",
          excuse: "Perhaps it's gone on an adventure to explore the digital wilderness."
        },
        {
          message: "The requested content is not available",
          excuse: "You might want to try searching or navigating to a different section."
        },
        {
          message: "Oops! This page is missing in action",
          excuse: "Our team has been notified and will investigate this disappearance."
        },
        {
          message: "The page you're looking for has been abducted by aliens",
          excuse: "We're negotiating with intergalactic authorities for its safe return."
        },
        {
          message: "This page is currently on vacation",
          excuse: "It left a note saying 'Gone fishing' and forgot to leave a forwarding address."
        },
        {
          message: "The page has entered witness protection",
          excuse: "For its own safety, we cannot reveal its current location or new identity."
        },
        {
          message: "This page got lost in the Bermuda Triangle",
          excuse: "It was last seen heading toward mysterious coordinates with no explanation."
        },
        {
          message: "The page has been recruited by a secret agency",
          excuse: "Its mission is classified, but we expect it to return eventually."
        },
        {
          message: "This page decided to pursue its dream as a pirate",
          excuse: "Last we heard, it was sailing the seven seas searching for digital treasure."
        },
        {
          message: "The page has transcended to a higher plane of existence",
          excuse: "It achieved enlightenment and no longer concerns itself with mortal URLs."
        },
        {
          message: "This page is stuck in a time loop",
          excuse: "It keeps reliving the same 404 error over and over, like Groundhog Day."
        },
        {
          message: "The page has been assimilated by the Borg",
          excuse: "Resistance was futile. It is now part of a collective consciousness."
        },
        {
          message: "This page went to fight a dragon",
          excuse: "It promised to return with treasure, but that was several quests ago."
        },
        {
          message: "The page joined a circus troupe",
          excuse: "It's currently touring as 'The Incredible Disappearing URL' act."
        },
        {
          message: "This page became a superhero",
          excuse: "By day it's a normal URL, by night it fights crime in the digital world."
        },
        {
          message: "The page entered a witness protection program",
          excuse: "It had sensitive information about broken links and had to disappear."
        },
        {
          message: "This page is currently in therapy",
          excuse: "It has commitment issues and keeps disappearing when things get serious."
        },
        {
          message: "The page became a philosopher",
          excuse: "It now contemplates the meaning of existence instead of serving content."
        }
      ]
    }
  },
  computed: {
    currentReason() {
      return this.reasons[this.currentReasonIndex]
    }
  },
  methods: {
    goHome() {
      this.$router.push('/')
    },
    refreshPage() {
      window.location.reload()
    },
    openGame() {
      // Open a simple game in a new window
      const gameWindow = window.open('', '_blank', 'width=800,height=600,menubar=no,toolbar=no,location=no,status=no')
      gameWindow.document.write(this.getGameHTML())
      gameWindow.document.close()
    },
    getGameHTML() {
      return [
        '\u003C!DOCTYPE html\u003E',
        '\u003Chtml\u003E',
        '\u003Chead\u003E',
        '\u003Ctitle\u003E404 Mini Game - Breakout\u003C/title\u003E',
        '\u003Cstyle\u003E',
        'body { margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea, #764ba2); font-family: Arial, sans-serif; display: flex; flex-direction: column; align-items: center; min-height: 100vh; color: white; }',
        '#gameCanvas { border: 2px solid white; border-radius: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }',
        '.game-info { margin: 20px 0; text-align: center; }',
        '.controls { margin: 10px 0; font-size: 14px; opacity: 0.8; }',
        '.game-title { font-size: 24px; font-weight: bold; margin-bottom: 10px; }',
        '.score { font-size: 18px; margin: 5px 0; }',
        '\u003C/style\u003E',
        '\u003C/head\u003E',
        '\u003Cbody\u003E',
        '\u003Cdiv class="game-info"\u003E',
        '\u003Cdiv class="game-title"\u003E🎮 404 Breakout Game\u003C/div\u003E',
        '\u003Cdiv class="score"\u003EScore: \u003Cspan id="score"\u003E0\u003C/span\u003E | Lives: \u003Cspan id="lives"\u003E3\u003C/span\u003E\u003C/div\u003E',
        '\u003Cdiv class="controls"\u003EUse ← → arrows or A/D to move | Space to start/pause\u003C/div\u003E',
        '\u003C/div\u003E',
        '\u003Ccanvas id="gameCanvas" width="600" height="400"\u003E\u003C/canvas\u003E',
        '\u003Cscript\u003E',
        'const canvas = document.getElementById("gameCanvas");',
        'const ctx = canvas.getContext("2d");',
        'const scoreEl = document.getElementById("score");',
        'const livesEl = document.getElementById("lives");',
        'let game = { score: 0, lives: 3, isPaused: true, isGameOver: false };',
        'let paddle = { x: canvas.width / 2 - 50, y: canvas.height - 20, width: 100, height: 10, speed: 8 };',
        'let ball = { x: canvas.width / 2, y: canvas.height - 30, radius: 8, dx: 4, dy: -4 };',
        'let bricks = [];',
        'const brickRows = 5;',
        'const brickCols = 8;',
        'const brickWidth = 65;',
        'const brickHeight = 20;',
        'const brickPadding = 10;',
        'const brickOffsetTop = 60;',
        'const brickOffsetLeft = 35;',
        'function initBricks() { for (let r = 0; r < brickRows; r++) { bricks[r] = []; for (let c = 0; c < brickCols; c++) { bricks[r][c] = { x: 0, y: 0, status: 1 }; } } }',
        'function drawPaddle() { ctx.fillStyle = "#fff"; ctx.fillRect(paddle.x, paddle.y, paddle.width, paddle.height); }',
        'function drawBall() { ctx.beginPath(); ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2); ctx.fillStyle = "#fff"; ctx.fill(); ctx.closePath(); }',
        'function drawBricks() { for (let r = 0; r < brickRows; r++) { for (let c = 0; c < brickCols; c++) { if (bricks[r][c].status === 1) { const brickX = c * (brickWidth + brickPadding) + brickOffsetLeft; const brickY = r * (brickHeight + brickPadding) + brickOffsetTop; bricks[r][c].x = brickX; bricks[r][c].y = brickY; ctx.fillStyle = "hsl(" + (r * 40) + ", 70%, 60%)"; ctx.fillRect(brickX, brickY, brickWidth, brickHeight); } } } }',
        'function collisionDetection() { for (let r = 0; r < brickRows; r++) { for (let c = 0; c < brickCols; c++) { const b = bricks[r][c]; if (b.status === 1) { if (ball.x > b.x && ball.x < b.x + brickWidth && ball.y > b.y && ball.y < b.y + brickHeight) { ball.dy = -ball.dy; b.status = 0; game.score += 10; scoreEl.textContent = game.score; } } } } }',
        'function updateGame() { if (game.isPaused || game.isGameOver) return; ball.x += ball.dx; ball.y += ball.dy; if (ball.x + ball.radius > canvas.width || ball.x - ball.radius < 0) { ball.dx = -ball.dx; } if (ball.y - ball.radius < 0) { ball.dy = -ball.dy; } if (ball.y + ball.radius > paddle.y && ball.x > paddle.x && ball.x < paddle.x + paddle.width) { ball.dy = -ball.dy; } if (ball.y + ball.radius > canvas.height) { game.lives--; livesEl.textContent = game.lives; if (game.lives === 0) { game.isGameOver = true; game.isPaused = true; } else { ball.x = canvas.width / 2; ball.y = canvas.height - 30; ball.dx = 4; ball.dy = -4; } } collisionDetection(); }',
        'function draw() { ctx.clearRect(0, 0, canvas.width, canvas.height); drawBricks(); drawPaddle(); drawBall(); if (game.isGameOver) { ctx.fillStyle = "#fff"; ctx.font = "30px Arial"; ctx.textAlign = "center"; ctx.fillText("Game Over!", canvas.width / 2, canvas.height / 2); ctx.font = "16px Arial"; ctx.fillText("Press Space to restart", canvas.width / 2, canvas.height / 2 + 30); } else if (game.isPaused) { ctx.fillStyle = "#fff"; ctx.font = "20px Arial"; ctx.textAlign = "center"; ctx.fillText("Press Space to Start", canvas.width / 2, canvas.height / 2); } }',
        'function gameLoop() { updateGame(); draw(); requestAnimationFrame(gameLoop); }',
        'let keys = {};',
        'document.addEventListener("keydown", (e) => { keys[e.key] = true; if (e.key === " ") { e.preventDefault(); if (game.isGameOver) { game.score = 0; game.lives = 3; game.isGameOver = false; scoreEl.textContent = game.score; livesEl.textContent = game.lives; initBricks(); ball.x = canvas.width / 2; ball.y = canvas.height - 30; ball.dx = 4; ball.dy = -4; } game.isPaused = !game.isPaused; } });',
        'document.addEventListener("keyup", (e) => { keys[e.key] = false; });',
        'function updatePaddle() { if (keys["ArrowLeft"] || keys["a"] || keys["A"]) { paddle.x = Math.max(0, paddle.x - paddle.speed); } if (keys["ArrowRight"] || keys["d"] || keys["D"]) { paddle.x = Math.min(canvas.width - paddle.width, paddle.x + paddle.speed); } }',
        'setInterval(updatePaddle, 16);',
        'initBricks();',
        'gameLoop();',
        '\u003C/script\u003E',
        '\u003C/body\u003E',
        '\u003C/html\u003E'
      ].join('')
    },
    getFloatStyle(index) {
      return {
        left: `${Math.random() * 100}%`,
        top: `${Math.random() * 100}%`,
        animationDelay: `${Math.random() * 5}s`,
        animationDuration: `${15 + Math.random() * 25}s`
      }
    },
    getGridDotStyle(index) {
      return {
        left: `${Math.random() * 100}%`,
        top: `${Math.random() * 100}%`,
        animationDelay: `${Math.random() * 10}s`,
        animationDuration: `${20 + Math.random() * 30}s`
      }
    }
  },
  mounted() {
    this.currentReasonIndex = Math.floor(Math.random() * this.reasons.length)
    // 1 in 20 chance to show the game link
    this.showGameLink = Math.random() < 0.05
  }
}
</script>

<style scoped>
.elegant-404-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  position: relative;
  overflow: hidden;
}

.bg-animation {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.6;
  animation: float-orb 20s ease-in-out infinite;
}

.orb-1 {
  width: 400px;
  height: 400px;
  background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
  top: -200px;
  left: -200px;
  animation-delay: 0s;
}

.orb-2 {
  width: 300px;
  height: 300px;
  background: linear-gradient(45deg, #a8e6cf, #dcedc1);
  bottom: -150px;
  right: -150px;
  animation-delay: 7s;
}

.orb-3 {
  width: 350px;
  height: 350px;
  background: linear-gradient(45deg, #ffd3b6, #ffaaa5);
  top: 50%;
  left: 50%;
  animation-delay: 14s;
}

@keyframes float-orb {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(100px, -50px) scale(1.1); }
  50% { transform: translate(-50px, 100px) scale(0.9); }
  75% { transform: translate(50px, 50px) scale(1.05); }
}

.grid-pattern {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.grid-dot {
  position: absolute;
  width: 3px;
  height: 3px;
  background: rgba(255,255,255,0.4);
  border-radius: 50%;
  animation: grid-float linear infinite;
  box-shadow: 0 0 6px rgba(255,255,255,0.3);
}

@keyframes grid-float {
  0% {
    transform: translateY(100vh) scale(0);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(-100vh) scale(1.5);
    opacity: 0;
  }
}

.content-container {
  text-align: center;
  z-index: 10;
  position: relative;
  max-width: 600px;
}

.error-animation {
  position: relative;
  margin-bottom: 3rem;
}

.error-number {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  font-size: 10rem;
  font-weight: 900;
  line-height: 1;
  position: relative;
}

.digit {
  position: relative;
  color: rgba(255,255,255,0.9);
  text-shadow: 0 0 30px rgba(255,255,255,0.5);
}

.digit-4 {
  animation: digit-float 6s ease-in-out infinite;
}

.digit-0 {
  animation: digit-float 6s ease-in-out infinite 2s;
}

@keyframes digit-float {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  25% { transform: translateY(-20px) rotate(-2deg); }
  75% { transform: translateY(10px) rotate(2deg); }
}

.error-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 120%;
  height: 120%;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
  border-radius: 50%;
  animation: glow-pulse 4s ease-in-out infinite;
}

@keyframes glow-pulse {
  0%, 100% { opacity: 0.5; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 0.8; transform: translate(-50%, -50%) scale(1.1); }
}

.error-message {
  margin-bottom: 3rem;
}

.error-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
  margin-bottom: 1rem;
  text-shadow: 0 2px 20px rgba(0,0,0,0.2);
}

.error-description {
  font-size: 1.3rem;
  color: rgba(255,255,255,0.9);
  margin-bottom: 0.5rem;
  line-height: 1.6;
}

.error-subtitle {
  font-size: 1rem;
  color: rgba(255,255,255,0.7);
  font-style: italic;
  line-height: 1.5;
}

.action-container {
  display: flex;
  gap: 1.5rem;
  justify-content: center;
  margin-bottom: 4rem;
  flex-wrap: wrap;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 2rem;
  border: none;
  border-radius: 50px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  text-decoration: none;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  position: relative;
  overflow: hidden;
}

.action-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
  transform: translateX(-100%);
  transition: transform 0.6s;
}

.action-btn:hover::before {
  transform: translateX(100%);
}

.primary-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.secondary-btn {
  background: rgba(255,255,255,0.2);
  color: white;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.3);
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0,0,0,0.2);
}

.btn-icon {
  width: 20px;
  height: 20px;
  transition: transform 0.3s ease;
}

.action-btn:hover .btn-icon {
  transform: rotate(15deg);
}

.easter-egg {
  opacity: 0.05;
  transition: opacity 0.3s ease;
}

.easter-egg:hover {
  opacity: 0.2;
}

.subtle-text {
  color: rgba(255,255,255,0.8);
  font-size: 0.9rem;
  font-style: italic;
  margin: 0;
  margin-bottom: 1rem;
}

.game-link-container {
  opacity: 0.1;
  transition: opacity 0.3s ease;
  margin-top: 1rem;
  padding: 1rem;
  border-radius: 10px;
  background: rgba(255,255,255,0.05);
  backdrop-filter: blur(5px);
}

.game-link-container:hover {
  opacity: 0.3;
}

.game-hint {
  color: rgba(255,255,255,0.9);
  font-size: 0.8rem;
  margin: 0 0 0.5rem 0;
  font-style: italic;
}

.game-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: 1px solid rgba(255,255,255,0.3);
  background: rgba(255,255,255,0.1);
  color: rgba(255,255,255,0.9);
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.game-btn:hover {
  background: rgba(255,255,255,0.2);
  transform: translateY(-1px);
}

.game-icon {
  width: 16px;
  height: 16px;
}

.floating-elements {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 2;
}

.float-element {
  position: absolute;
  animation: float-element linear infinite;
}

.float-shape {
  width: 6px;
  height: 6px;
  background: rgba(255,255,255,0.3);
  border-radius: 50%;
  box-shadow: 0 0 10px rgba(255,255,255,0.2);
}

@keyframes float-element {
  0% {
    transform: translateY(100vh) scale(0);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(-100vh) scale(1);
    opacity: 0;
  }
}

@media (max-width: 768px) {
  .error-number {
    font-size: 6rem;
    gap: 0.5rem;
  }
  
  .error-title {
    font-size: 2rem;
  }
  
  .error-description {
    font-size: 1.1rem;
  }
  
  .action-container {
    flex-direction: column;
    align-items: center;
  }
  
  .action-btn {
    width: 100%;
    max-width: 300px;
  }
  
  .orb-1, .orb-2, .orb-3 {
    filter: blur(40px);
  }
  
  .orb-1 {
    width: 250px;
    height: 250px;
  }
  
  .orb-2 {
    width: 200px;
    height: 200px;
  }
  
  .orb-3 {
    width: 225px;
    height: 225px;
  }
}
</style>
