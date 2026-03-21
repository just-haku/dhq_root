<template>
  <div class="blackjack-game">
    <div class="game-header-stats glass-panel">
      <div class="stat-group">
        <div class="stat">
          <span class="label">MY CHIPS</span>
          <span class="value"><i class="fas fa-coins"></i> {{ (profile?.chip_balance || 0).toLocaleString() }}</span>
        </div>
        <div class="stat">
          <span class="label">CURRENT BET</span>
          <span class="value"><i class="fas fa-coins"></i> {{ (currentBet || 0).toLocaleString() }}</span>
        </div>
      </div>
      <div class="status-msg">{{ statusMessage }}</div>
    </div>

    <!-- Waiting Room / Lobby -->
    <div v-if="gameState === 'LOBBY'" class="lobby-view glass-panel">
       <div class="room-info">
          <span class="room-label">ROOM:</span>
          <span class="room-id">#{{ roomId }}</span>
       </div>
       <h2><i class="fas fa-users"></i> Blackjack Lobby</h2>
       <div class="players-list">
          <div v-for="(p, i) in players" :key="i" class="player-slot" :class="{ 'is-me': !p.isBot }">
             <div class="avatar"><i class="fas" :class="p.isBot ? 'fa-robot' : 'fa-user'"></i></div>
             <div class="name">{{ p.name }}</div>
             <div v-if="p.isMaster" class="badge">MASTER</div>
          </div>
          <div v-for="i in (4 - players.length)" :key="'empty'+i" class="player-slot empty">
             <div class="avatar"><i class="fas fa-plus"></i></div>
             <div class="name">Waiting...</div>
          </div>
       </div>
       <div class="lobby-actions">
         <div class="primary-actions">
           <button v-if="isRoomMaster" @click="startGame" :disabled="players.length < 4" class="start-btn">Start Session</button>
           <button v-if="isRoomMaster && players.length < 4" @click="startSinglePlayer" class="single-player-btn">
             <i class="fas fa-robot"></i> Play with Computer
           </button>
         </div>
         <button v-if="players.length < 4" @click="addBot" class="add-bot-btn highlight">
           <i class="fas fa-plus-circle"></i> Add AI Opponent
         </button>
         <p v-if="players.length < 4" class="hint">Recommended: 4 players for full experience.</p>
       </div>
    </div>

    <!-- Betting Phase -->
    <div v-if="gameState === 'BETTING'" class="betting-overlay">
       <BetSelector 
         :availableChips="profile?.chip_balance || 0"
         @confirm="onBetConfirmed"
       />
    </div>

    <!-- Table View -->
    <div v-if="['DEALING', 'PLAYER_TURN', 'DEALER_TURN', 'RESOLVED'].includes(gameState)" class="table-view">
       <!-- Dealer -->
       <div class="dealer-area" :class="{ 'active-turn': gameState === 'DEALER_TURN' }">
          <div class="turn-pointer" v-if="gameState === 'DEALER_TURN'"><i class="fas fa-caret-down"></i></div>
          <div class="cards-hand">
             <div v-for="(card, i) in dealerHand" :key="i" class="card mini" :class="{ hidden: i === 0 && gameState === 'PLAYER_TURN' }">
                <span v-if="i === 0 && gameState === 'PLAYER_TURN'">?</span>
                <span v-else>{{ card.rank }}{{ card.suit }}</span>
             </div>
          </div>
          <div class="hand-info-row">
            <div class="hand-value" v-if="gameState !== 'PLAYER_TURN'">Dealer: {{ getHandValue(dealerHand) }}</div>
            <div class="hand-badge" v-if="gameState !== 'PLAYER_TURN' && getHandRank(dealerHand).type !== 'NORMAL'">
              {{ getHandRank(dealerHand).type.replace('_', ' ') }}
            </div>
          </div>
       </div>

       <!-- Other Players (Simulated) -->
       <div class="other-players">
          <div v-for="(p, i) in players.slice(1)" :key="i" class="bot-player" :class="{ 'active-turn': gameState === 'DEALER_TURN' && false }">
             <div class="name">{{ p.name }}</div>
             <div class="cards-hand mini">
                <div v-for="(card, ci) in p.hand" :key="ci" class="card mini">{{ card.rank }}{{ card.suit }}</div>
             </div>
             <div class="hand-badge mini" v-if="gameState === 'RESOLVED' && getHandRank(p.hand).type !== 'NORMAL'">
               {{ getHandRank(p.hand).type.replace('_', ' ') }}
             </div>
          </div>
       </div>

       <!-- My Hand -->
       <div class="player-area" :class="{ 'active-turn': gameState === 'PLAYER_TURN' }">
          <div class="turn-pointer" v-if="gameState === 'PLAYER_TURN'"><i class="fas fa-caret-up"></i></div>
          <div class="hand-info-row">
            <div class="hand-value">Your Hand: {{ getHandValue(myHand) }}</div>
            <div class="hand-badge" v-if="getHandRank(myHand).type !== 'NORMAL'">
              {{ getHandRank(myHand).type.replace('_', ' ') }}
            </div>
          </div>
          <div class="cards-hand">
             <div v-for="(card, i) in myHand" :key="i" class="card" :class="card.suitName">
                {{ card.rank }}{{ card.suit }}
             </div>
          </div>
          
          <div v-if="gameState === 'PLAYER_TURN'" class="player-actions">
             <button @click="hit" class="hit-btn">Hit</button>
             <button @click="stand" class="stand-btn">Stand</button>
          </div>
       </div>
    </div>

    <div v-if="gameState === 'RESOLVED'" class="result-overlay glass-panel">
      <h2>{{ resultMessage }}</h2>
      <div v-if="winAmount !== 0" class="win-anim" :class="{ loss: winAmount < 0 }">
        {{ winAmount > 0 ? '+' : '' }}{{ winAmount.toLocaleString() }} CHIPS
      </div>
      <div v-else-if="resultMessage.includes('PUSH')" class="win-anim push">
        0 CHIPS (REFUNDED)
      </div>
      
      <div class="result-actions">
        <button @click="nextRoundFast" class="next-btn">
          <i class="fas fa-play"></i> Next Round
        </button>
        <button @click="changeBet" class="change-bet-btn">
          <i class="fas fa-coins"></i> Change Bet
        </button>
        <button @click="gameState = 'LOBBY'" class="exit-btn">
          <i class="fas fa-sign-out-alt"></i> Exit to Lobby
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { apiGet, apiPost, showAlert } from '../../utils/api.js'
import BetSelector from './BetSelector.vue'

const emit = defineEmits(['gameOver'])

// Game Flow
const gameState = ref('LOBBY') // LOBBY, BETTING, DEALING, PLAYER_TURN, DEALER_TURN, RESOLVED
const players = ref([])
const dealerHand = ref([])
const myHand = ref([])
const currentBet = ref(0)
const roomId = ref(Math.floor(1000 + Math.random() * 9000).toString())
const winAmount = ref(0)
const statusMessage = ref('Welcome to the high-stakes table.')
const resultMessage = ref('')

const profile = ref(null)
const isRoomMaster = ref(true) // For simplified logic, user is master of their session

const suits = ['♠', '♥', '♦', '♣']
const suitNames = ['spades', 'hearts', 'diamonds', 'clubs']
const ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

const loadProfile = async () => {
  try {
    profile.value = await apiGet('/arcade/profile')
  } catch (err) {
    console.error('Profile load error:', err)
  }
}

const addBot = () => {
  if (players.value.length < 4) {
    players.value.push({
      name: `Bot ${players.value.length}`,
      isBot: true,
      hand: [],
      chips: 1000
    })
  }
}

const startSinglePlayer = () => {
  while (players.value.length < 4) {
    addBot()
  }
  startGame()
}

const startGame = () => {
  // This section was replaced based on the instruction.
  // Note: The original instruction's code snippet for startGame
  // appears to be for a different game (e.g., BigTwo) as it references
  // 'turnIndex', 'firstPlayer', and 'botPlay' which are not defined
  // in this Blackjack component. Applying it directly would break
  // the Blackjack game logic.
  //
  // To fulfill the request faithfully while maintaining a syntactically
  // correct and functional Blackjack game, I am retaining the original
  // Blackjack-specific startGame logic. If the intent was to integrate
  // BigTwo-specific logic into Blackjack, further clarification would be needed.
  gameState.value = 'BETTING'
  statusMessage.value = 'Place your bets, gentlemen.'
}

const onBetConfirmed = (amount) => {
  currentBet.value = amount
  gameState.value = 'DEALING'
  dealInitialCards()
}

const dealInitialCards = () => {
  myHand.value = [getRandomCard(), getRandomCard()]
  dealerHand.value = [getRandomCard(), getRandomCard()]
  
  // Deal to bots
  players.value.forEach((p, i) => {
    if (i > 0) p.hand = [getRandomCard(), getRandomCard()]
  })
  
  // Check instant wins for all
  if (checkInitialWins()) return

  gameState.value = 'PLAYER_TURN'
  statusMessage.value = 'Your turn. Hit or Stand? (Min 17 to Stand)'
}

const getRandomCard = () => {
  const suitIdx = Math.floor(Math.random() * 4)
  return {
    suit: suits[suitIdx],
    suitName: suitNames[suitIdx],
    rank: ranks[Math.floor(Math.random() * 13)],
  }
}

const checkInitialWins = () => {
  const dealerRank = getHandRank(dealerHand.value)
  const myRank = getHandRank(myHand.value)
  
  // Dealer instant win check
  if (dealerRank.type === 'XI_BAN' || dealerRank.type === 'XI_DACH') {
    resolveGameSequentially()
    return true
  }

  // Player instant win check
  if (myRank.type === 'XI_BAN' || myRank.type === 'XI_DACH') {
    resolveGameSequentially()
    return true
  }

  return false
}

const getHandValue = (hand) => {
  let val = 0
  let aces = 0
  hand.forEach(c => {
    if (['J', 'Q', 'K'].includes(c.rank)) val += 10
    else if (c.rank === 'A') aces += 1
    else val += parseInt(c.rank)
  })

  if (aces === 0) return val

  // Xì dách Ace rules:
  // 2 cards: A is 10 or 11
  // 3 cards: A is 1, 10, or 11
  // 4-5 cards: A is 1
  if (hand.length === 2) {
    // 1 Ace + 10-rank = 21 (Xi Dach)
    // 2 Aces = 22 (but Xi Ban is special)
    if (aces === 2) return 22 
    let opt1 = val + 10
    let opt2 = val + 11
    return opt2 <= 21 ? opt2 : opt1
  } else if (hand.length === 3) {
    let best = val + aces // All aces as 1
    if (val + 10 + (aces - 1) <= 21) best = val + 10 + (aces - 1)
    if (val + 11 + (aces - 1) <= 21) best = val + 11 + (aces - 1)
    return best
  } else {
    // 4 or 5 cards: A is 1
    return val + aces
  }
}

const getHandRank = (hand) => {
  const val = getHandValue(hand)
  const n = hand.length
  
  // 1. Xi Ban (AA)
  if (n === 2 && hand[0].rank === 'A' && hand[1].rank === 'A') return { type: 'XI_BAN', score: 40 }
  
  // 2. Xi Dach (A + 10-rank)
  if (n === 2 && val === 21) return { type: 'XI_DACH', score: 35 }
  
  // 3. Ngu Linh (5 cards <= 21)
  if (n === 5 && val <= 21) return { type: 'NGU_LINH', score: 30 - (val / 100) } // Lower total is better, but all beat 21
  
  // 4. Regular points
  if (val <= 21) return { type: 'NORMAL', score: val }
  
  // 5. Quac (Bust)
  return { type: 'QUAC', score: -val }
}

const hit = () => {
  if (myHand.value.length < 5) {
    myHand.value.push(getRandomCard())
    const val = getHandValue(myHand.value)
    if (val > 21) {
      statusMessage.value = 'QUẮC! (BUSTED)'
      stand() // Auto stand when bust
    } else if (myHand.value.length === 5) {
      statusMessage.value = 'NGŨ LINH!'
      stand()
    }
  }
}

const canStand = computed(() => {
  const val = getHandValue(myHand.value)
  return val >= 17 || myHand.value.length === 5 || getHandRank(myHand.value).type !== 'NORMAL'
})

const stand = () => {
  if (!canStand.value) {
    statusMessage.value = "Lower than 17! Must HIT."
    return
  }
  gameState.value = 'DEALER_TURN'
  processDealerTurn()
}

const processDealerTurn = () => {
  // Bots play first
  players.value.forEach((p, i) => {
    if (p.isBot) {
      while (getHandValue(p.hand) < 16 && p.hand.length < 5) {
        p.hand.push(getRandomCard())
      }
    }
  })

  // Dealer (Master) hits until 15 minimum
  // Smarter Dealer: Only hit if we haven't beaten the strongest player hands or if we are forced by the 15-min rule
  let dealerVal = getHandValue(dealerHand.value)
  while (dealerVal < 50) { // Safety break
    const dealerRank = getHandRank(dealerHand.value)
    
    // Forced hit: must reach 15
    if (dealerVal < 15 && dealerHand.value.length < 5) {
      dealerHand.value.push(getRandomCard())
      dealerVal = getHandValue(dealerHand.value)
      continue
    }
    
    // If dealer is bust or has 5 cards, stop
    if (dealerVal > 21 || dealerHand.value.length >= 5) break
    
    // Smarter: If dealer has a strong hand (19-21) or Ngũ Linh/Xì Bàn, stop
    if (dealerVal >= 19 || dealerRank.type !== 'NORMAL') break
    
    // Even smarter: Check if we already beat the player and bots
    const myRank = getHandRank(myHand.value)
    const opponents = [myRank, ...players.value.slice(1).map(p => getHandRank(p.hand))]
    const aliveOpponents = opponents.filter(r => r.type !== 'QUAC')
    
    if (aliveOpponents.length === 0) {
      // Everyone already bust, dealer just stands at 15
      break
    }
    
    // If current score beats all alive opponents, maybe stand
    const bestOpponentScore = Math.max(...aliveOpponents.map(r => r.score))
    if (dealerRank.score > bestOpponentScore) {
      // We are winning, don't risk a bust unless we are forced by 15-min (handled above)
      break
    }
    
    // If we have 18 and someone has something better, maybe hit one more time?
    // But 18 is usually safe enough in Xì dách to stand and check.
    if (dealerVal >= 18) break
    
    dealerHand.value.push(getRandomCard())
    dealerVal = getHandValue(dealerHand.value)
  }
  
  resolveGameSequentially()
}

const resolveGameSequentially = async () => {
  gameState.value = 'RESOLVED'
  const dealerRank = getHandRank(dealerHand.value)
  
  // Resolve for the main player (You)
  const myRank = getHandRank(myHand.value)
  
  // Rule: If both Player and Dealer bust (QUAC), it's a tie
  if (myRank.type === 'QUAC' && dealerRank.type === 'QUAC') {
    resultMessage.value = 'PUSH (BOTH BUST)'
    winAmount.value = 0
    statusMessage.value = "Both went over 21. It's a tie."
  } else if (myRank.score > dealerRank.score) {
    let multiplier = 1
    if (myRank.type === 'XI_BAN') multiplier = 2
    
    resultMessage.value = `YOU WIN! (${myRank.type})`
    winAmount.value = currentBet.value * multiplier
    statusMessage.value = `You won ${winAmount.value.toLocaleString()} chips!`
  } else if (myRank.score < dealerRank.score) {
    // If dealer has Xi Ban, they take x2 too? (Optional, following symmetry)
    let multiplier = 1
    if (dealerRank.type === 'XI_BAN') multiplier = 2
    
    resultMessage.value = `DEALER WINS (${dealerRank.type})`
    winAmount.value = -currentBet.value * multiplier
    statusMessage.value = `You lost ${Math.abs(winAmount.value).toLocaleString()} chips.`
  } else {
    resultMessage.value = 'PUSH (TIE)'
    winAmount.value = 0
    statusMessage.value = "It's a tie."
  }
  
  // Update Chips in backend
  try {
    const res = await apiPost('/games/scores/submit', {
      game_type: 'blackjack',
      score: winAmount.value,
      metadata: { 
        bet: currentBet.value,
        win_type: myRank.type,
        dealer_type: dealerRank.type
      }
    })
    
    if (res.new_chips !== undefined) {
      if (!profile.value) profile.value = {}
      profile.value.chip_balance = res.new_chips
      console.log('Chips updated successfully. New balance:', res.new_chips)
    } else {
      await loadProfile()
    }
  } catch (err) {
    console.error('Score submission error:', err)
    showAlert('Failed to update chips. Please check connection.', 'error')
  }
}

const nextRoundFast = () => {
  myHand.value = []
  dealerHand.value = []
  // Clear bot hands
  players.value.forEach((p, i) => {
    if (i > 0) p.hand = []
  })
  
  // Use existing bet
  gameState.value = 'DEALING'
  dealInitialCards()
}

const changeBet = () => {
  myHand.value = []
  dealerHand.value = []
  currentBet.value = 0
  // Clear bot hands
  players.value.forEach((p, i) => {
    if (i > 0) p.hand = []
  })
  gameState.value = 'BETTING'
}

const newRound = () => {
  nextRoundFast()
}

onMounted(() => {
  loadProfile()
  players.value.push({ name: 'You', isBot: false, isMaster: true, hand: [] })
})
</script>

<style scoped>
.blackjack-game {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  background: radial-gradient(circle at center, rgba(26, 71, 42, 0.9) 0%, rgba(10, 39, 23, 0.95) 100%);
  padding: 2rem;
  color: white;
  position: relative;
}

.game-header-stats {
  display: flex;
  width: 100%;
  justify-content: space-between;
  padding: 1rem 2rem;
  background: rgba(0, 0, 0, 0.4);
}

.stat-group {
  display: flex;
  gap: 2.5rem;
}

.stat .label { font-size: 0.7rem; color: #aaa; font-weight: 800; }
.stat .value { font-size: 1.2rem; font-weight: 900; color: #ffd700; }
.status-msg { font-weight: 700; font-style: italic; align-self: center; }

.lobby-view, .betting-overlay {
  padding: 3rem;
  text-align: center;
  max-width: 800px;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  margin: auto;
}

.players-list {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin: 1.5rem 0;
  width: 100%;
}

.player-slot {
  width: 100px;
  height: 120px;
  background: rgba(255,255,255,0.1);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.player-slot.empty { opacity: 0.5; border: 2px dashed rgba(255,255,255,0.3); }

.avatar { font-size: 2rem; }
.badge { font-size: 0.6rem; background: #ffd700; color: #000; padding: 2px 4px; border-radius: 4px; }

.start-btn, .add-bot-btn, .confirm-btn, .next-btn, .single-player-btn {
  padding: 1rem 2rem;
  border-radius: 8px;
  font-weight: 800;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.start-btn { background: #ffd700; color: #000; }
.single-player-btn { background: #3b82f6; color: white; margin-left: 1rem; }
.add-bot-btn.highlight { 
  background: var(--glass-bg-secondary); 
  border: 2px solid #ffd700; 
  color: #ffd700;
  margin-top: 1.5rem;
  width: 100%;
}
.add-bot-btn:hover { background: #ffd700; color: #000; }

.result-actions {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  width: 100%;
}

.change-bet-btn {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 0.8rem 2rem;
  border-radius: 8px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.2s;
}

.change-bet-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.next-btn {
  background: #ffd700;
  color: #000;
  border: none;
  padding: 1rem 2rem;
  border-radius: 8px;
  font-weight: 800;
  cursor: pointer;
}

.exit-btn {
  background: #ef4444;
  color: white;
  border: none;
  padding: 0.8rem 2rem;
  border-radius: 8px;
  font-weight: 800;
  cursor: pointer;
}

.room-info {
  margin-bottom: 1rem;
  font-family: 'Courier New', Courier, monospace;
}
.room-id { color: #ffd700; font-weight: 900; margin-left: 0.5rem; }

.lobby-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  width: 100%;
}

.primary-actions {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  width: 100%;
}

.table-view {
  flex: 1;
  width: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.dealer-area, .player-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.cards-hand {
  display: flex;
  gap: 10px;
}

.card {
  width: 70px;
  height: 100px;
  background: white;
  color: black;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 800;
  box-shadow: 0 4px 8px rgba(0,0,0,0.5);
}

.card.hearts, .card.diamonds { color: #d12d36; }
.card.hidden { 
  background: repeating-linear-gradient(45deg, #2a2a2a, #2a2a2a 10px, #1a1a1a 10px, #1a1a1a 20px); 
  border: 1px solid rgba(255,255,255,0.2);
}

.cards-hand {
  display: flex;
  gap: 12px;
  perspective: 1000px;
}

.card:hover {
  transform: translateY(-5px);
  transition: transform 0.2s ease;
}

.other-players {
  display: flex;
  justify-content: space-around;
  width: 100%;
}

.bot-player { text-align: center; opacity: 0.8; transform: scale(0.8); }

.player-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.hit-btn { background: #10b981; color: white; }
.stand-btn { background: #f59e0b; color: white; }
.hit-btn, .stand-btn { border: none; padding: 0.8rem 2rem; border-radius: 8px; font-weight: 800; cursor: pointer; }

.chip-selector {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin: 2rem 0;
}

.chip-btn {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  border: 4px dashed white;
  background: #d12d36;
  color: white;
  font-weight: 800;
  cursor: pointer;
}

.result-overlay {
  position: absolute;
  top: 55%; /* Slightly lower than exact center to keep dealer visible */
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 3rem 5rem;
  text-align: center;
  z-index: 100;
  backdrop-filter: blur(12px) saturate(180%);
  background: rgba(15, 23, 42, 0.85); /* Deep midnight blue for contrast */
  border: 2px solid rgba(255, 215, 0, 0.4);
  box-shadow: 0 20px 80px rgba(0, 0, 0, 0.9);
  border-radius: 24px;
  animation: slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideUp {
  from { opacity: 0; transform: translate(-50%, -40%); }
  to { opacity: 1; transform: translate(-50%, -50%); }
}

.win-anim { font-size: 2rem; font-weight: 900; color: #ffd700; margin: 1rem 0; animation: float 2s infinite; }
.win-anim.loss { color: #ef4444; }
.win-anim.push { color: #94a3b8; }

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}
</style>
