<template>
  <div class="bigtwo-game">
    <div class="game-header-stats glass-panel">
      <div class="stat">
        <span class="label">MY CHIPS</span>
        <span class="value"><i class="fas fa-coins"></i> {{ (profile?.chip_balance || 0).toLocaleString() }}</span>
      </div>
      <div class="stat" v-if="currentBet > 0">
        <span class="label">CURRENT BET</span>
        <span class="value"><i class="fas fa-coins"></i> {{ currentBet.toLocaleString() }}</span>
      </div>
      <div class="status-msg">{{ statusMessage }}</div>
    </div>

    <!-- Lobby -->
    <div v-if="gameState === 'LOBBY'" class="lobby-view glass-panel">
       <div class="room-info">
          <span class="room-label">ROOM:</span>
          <span class="room-id">#{{ roomId }}</span>
       </div>
       <h2><i class="fas fa-cards"></i> Big Two Lobby</h2>
       <div class="players-list">
          <div v-for="(p, i) in players" :key="i" class="player-slot" :class="{ 'is-me': !p.isBot }">
             <div class="avatar"><i class="fas" :class="p.isBot ? 'fa-robot' : 'fa-user'"></i></div>
             <div class="name">{{ p.name }}</div>
          </div>
          <div v-for="i in (4 - players.length)" :key="'empty'+i" class="player-slot empty">
             <div class="avatar"><i class="fas fa-plus"></i></div>
             <div class="name">Waiting...</div>
          </div>
       </div>
       <div class="lobby-actions">
         <div class="primary-actions">
           <button @click="startGame" :disabled="players.length < 2" class="start-btn">Start Session</button>
           <button v-if="players.length < 4" @click="startSinglePlayer" class="single-player-btn">
             <i class="fas fa-robot"></i> Play vs AI
           </button>
         </div>
         <button @click="addBot" v-if="players.length < 4" class="add-bot-btn highlight">
           <i class="fas fa-plus-circle"></i> Add AI Bot
         </button>
       </div>
    </div>

    <!-- Betting Phase -->
    <div v-if="gameState === 'BETTING'" class="betting-overlay">
       <BetSelector 
         :availableChips="profile?.chip_balance || 0"
         @confirm="onBetConfirmed"
       />
    </div>

    <!-- Game Table -->
    <div v-if="['PLAYING', 'RESOLVED'].includes(gameState)" class="table-view">
       <!-- Opponents -->
       <div class="opponents-layer">
          <div v-for="(p, i) in players.slice(1)" :key="i" class="opponent-slot" :class="['opp-' + i, { 'active-turn': turnIndex === i + 1 }]">
             <div class="turn-pointer" v-if="turnIndex === i + 1"><i class="fas fa-caret-down"></i></div>
             <div class="name">{{ p.name }} ({{ p.hand.length }} cards)</div>
             <div class="cards-back">
                <div v-for="c in Math.min(p.hand.length, 5)" :key="c" class="card-back"></div>
             </div>
          </div>
       </div>

       <!-- Last Played Combo -->
       <div class="last-played-area">
          <div v-if="lastCombo" class="last-combo glass-panel">
             <div class="played-by">{{ lastPlayerName }} played:</div>
             <div class="cards-hand collated">
                <div v-for="(card, i) in lastCombo.cards" 
                     :key="i" 
                     class="card mini layered" 
                     :class="card.suitName"
                     :style="{ '--index': i }">
                   <div class="card-content">
                     <span class="rank">{{ card.rank }}</span>
                     <span class="suit">{{ card.suit }}</span>
                   </div>
                </div>
             </div>
             <div class="combo-type">{{ lastCombo.type }}</div>
          </div>
          <div v-else class="last-combo empty">Fresh Start</div>
       </div>

       <!-- My Hand -->
       <div class="my-player-area">
          <div class="my-hand-container">
             <div v-for="(card, i) in myHand" :key="i" 
                  class="card" 
                  :class="[card.suitName, { selected: isSelected(i) }]"
                  @click="toggleSelect(i)">
                {{ card.rank }}{{ card.suit }}
             </div>
          </div>
          
          <div v-if="isMyTurn" class="player-actions">
             <button @click="playSelected" :disabled="!isValidMove" class="play-btn">Play Cards</button>
             <button @click="passTurn" :disabled="!lastCombo" class="pass-btn">Pass</button>
          </div>
       </div>
    </div>

    <!-- Result -->
    <div v-if="gameState === 'RESOLVED'" class="result-overlay glass-panel">
       <h2>{{ winnerIndex === 0 ? 'YOU WIN!' : players[winnerIndex].name + ' WINS!' }}</h2>
       <div class="reward" v-if="winAmount !== 0" :class="{ loss: winAmount < 0 }">
         {{ winAmount > 0 ? '+' : '' }}{{ winAmount.toLocaleString() }} CHIPS
       </div>
       <button @click="gameState = 'LOBBY'; currentBet = 0" class="exit-btn">Back to Lobby</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { apiGet, apiPost, showAlert } from '../../utils/api.js'
import BetSelector from './BetSelector.vue'

const emit = defineEmits(['gameOver'])

// Card config
const suits = ['♠', '♣', '♦', '♥'] // Spades < Clubs < Diamonds < Hearts
const suitNames = ['spades', 'clubs', 'diamonds', 'hearts']
const ranks = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2'] // 3 is lowest, 2 is highest

// Game State
const gameState = ref('LOBBY')
const players = ref([])
const myHand = ref([])
const selectedIndices = ref([])
const lastCombo = ref(null)
const lastPlayerIndex = ref(-1)
const roomId = ref(Math.floor(1000 + Math.random() * 9000).toString())
const statusMessage = ref('Welcome to Big Two.')
const winnerIndex = ref(-1)
const currentBet = ref(0)
const winAmount = ref(0)

const profile = ref(null)
const loadProfile = async () => {
  try {
    profile.value = await apiGet('/arcade/profile')
  } catch (err) {
    console.error('Profile load error:', err)
  }
}

const isMyTurn = computed(() => turnIndex.value === 0 && gameState.value === 'PLAYING')
const lastPlayerName = computed(() => lastPlayerIndex.value === -1 ? 'None' : players.value[lastPlayerIndex.value].name)

const startSinglePlayer = () => {
  while (players.value.length < 4) {
    addBot()
  }
  startGame()
}
const turnIndex = ref(0)
const addBot = () => {
  if (players.value.length < 4) {
    players.value.push({ name: `Bot ${players.value.length}`, isBot: true, hand: [] })
  }
}

const startGame = () => {
  gameState.value = 'BETTING'
  statusMessage.value = 'Place your bets.'
}

const onBetConfirmed = (amount) => {
  currentBet.value = amount
  gameState.value = 'PLAYING'
  dealCards()
}

const dealCards = () => {
  const deck = []
  ranks.forEach((r, ri) => {
    suits.forEach((s, si) => {
      deck.push({ rank: r, suit: s, suitName: suitNames[si], rankVal: ri, suitVal: si })
    })
  })
  
  // Shuffle
  for (let i = deck.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [deck[i], deck[j]] = [deck[j], deck[i]];
  }
  
  // Distribute
  players.value.forEach((p, i) => {
    p.hand = deck.slice(i * 13, (i + 1) * 13).sort((a, b) => a.rankVal - b.rankVal || a.suitVal - b.suitVal)
  })
  
  myHand.value = players.value[0].hand
  
  // Who goes first? (3 of Diamonds)
  const firstPlayer = players.value.findIndex(p => p.hand.some(c => c.rank === '3' && c.suit === '♦'))
  turnIndex.value = firstPlayer !== -1 ? firstPlayer : 0
  statusMessage.value = players.value[turnIndex.value].name + "'s turn"
  
  // Check for instant wins (Rule 3)
  if (checkInstantWin()) return

  if (players.value[turnIndex.value].isBot) {
    setTimeout(botPlay, 1000)
  }
}

const checkInstantWin = () => {
  for (let i = 0; i < players.value.length; i++) {
    const p = players.value[i]
    const hand = p.hand
    
    // Rule 3 conditions
    const ranksCount = {}
    hand.forEach(c => ranksCount[c.rank] = (ranksCount[c.rank] || 0) + 1)
    
    const isFourTwos = ranksCount['2'] === 4
    
    // Check for 6 pairs (any pairs for simplicity, matching user's "6 pairs" mention)
    let totalPairs = 0
    Object.values(ranksCount).forEach(count => { totalPairs += Math.floor(count / 2) })
    const isSixPairs = totalPairs >= 6
    
    let fourOfAKindCount = 0
    Object.values(ranksCount).forEach(count => { if (count === 4) fourOfAKindCount++ })
    const isThreeFourOfAKind = fourOfAKindCount >= 3
    
    const hasNoHighCards = !hand.some(c => ['J', 'Q', 'K'].includes(c.rank))
    
    const hasAllRanks = ranks.slice(0, 12).every(r => ranksCount[r] > 0) // 3 to A
    
    if (isFourTwos || isSixPairs || isThreeFourOfAKind || hasNoHighCards || hasAllRanks) {
      gameState.value = 'RESOLVED'
      winnerIndex.value = i
      // Standard win amount for instant win
      winAmount.value = (i === 0) ? currentBet.value : -currentBet.value
      statusMessage.value = `INSTANT WIN! ${p.name} has a special hand!`
      submitScore()
      return true
    }
  }
  return false
}

const toggleSelect = (i) => {
  const idx = selectedIndices.value.indexOf(i)
  if (idx === -1) selectedIndices.value.push(i)
  else selectedIndices.value.splice(idx, 1)
}

const isSelected = (i) => selectedIndices.value.includes(i)

const isValidMove = computed(() => {
  const selectedCards = selectedIndices.value.map(i => myHand.value[i]).sort((a,b) => a.rankVal - b.rankVal)
  if (selectedCards.length === 0) return false
  
  const combo = detectCombo(selectedCards)
  if (!combo) return false
  
  if (!lastCombo.value || lastPlayerIndex.value === 0) return true
  
  return canBeat(combo, lastCombo.value)
})

const detectCombo = (cards) => {
  const n = cards.length
  if (n === 0) return null
  
  // Sort cards by rank value for easier detection
  const sorted = [...cards].sort((a, b) => a.rankVal - b.rankVal)
  
  // Single, Pair, Triple, FourOfAKind (same rank)
  const isAllSameRank = sorted.every(c => c.rank === sorted[0].rank)
  if (isAllSameRank) {
    if (n === 1) return { type: 'Single', rank: sorted[0].rankVal, suit: sorted[0].suitVal, cards: sorted }
    if (n === 2) return { type: 'Pair', rank: sorted[0].rankVal, suit: Math.max(sorted[0].suitVal, sorted[1].suitVal), cards: sorted }
    if (n === 3) return { type: 'Triple', rank: sorted[0].rankVal, cards: sorted }
    if (n === 4) return { type: 'FourOfAKind', rank: sorted[0].rankVal, cards: sorted }
  }

  // Straight (Sảnh): 3+ consecutive ranks. 2 is NOT allowed in straights in Tien Len.
  if (n >= 3) {
    let isStraight = true
    for (let i = 0; i < n - 1; i++) {
      if (sorted[i+1].rankVal !== sorted[i].rankVal + 1 || sorted[i+1].rank === '2') {
        isStraight = false
        break
      }
    }
    if (isStraight && sorted[0].rank !== '2') {
      return { type: 'Straight', rank: sorted[n-1].rankVal, suit: sorted[n-1].suitVal, cards: sorted, length: n }
    }
  }

  // Pairs of Pine (Đôi thông): 3+ consecutive pairs.
  if (n >= 6 && n % 2 === 0) {
    let isPine = true
    for (let i = 0; i < n; i += 2) {
      if (sorted[i].rank !== sorted[i+1].rank) isPine = false
      if (i > 0 && sorted[i].rankVal !== sorted[i-2].rankVal + 1) isPine = false
      if (sorted[i].rank === '2') isPine = false
    }
    if (isPine) {
      return { type: 'PairsOfPine', rank: sorted[n-1].rankVal, suit: sorted[n-1].suitVal, cards: sorted, length: n / 2 }
    }
  }

  return null
}

const canBeat = (newC, oldC) => {
  // Case 1: Same type, different ranks/suits
  if (newC.type === oldC.type) {
    if (newC.type === 'Straight' || newC.type === 'PairsOfPine') {
      if (newC.length !== oldC.length) return false
    }
    if (newC.rank > oldC.rank) return true
    if (newC.rank === oldC.rank && (newC.suit || 0) > (oldC.suit || 0)) return true
    return false
  }

  // Special Rules (Rule 2): Cutting 2s
  if (oldC.type === 'Single' && oldC.cards[0].rank === '2') {
    if (newC.type === 'FourOfAKind') return true
    if (newC.type === 'PairsOfPine' && newC.length >= 3) return true
  }
  
  if (oldC.type === 'Pair' && oldC.cards[0].rank === '2') {
    if (newC.type === 'FourOfAKind') return true
    if (newC.type === 'PairsOfPine' && newC.length >= 4) return true
  }

  // FourOfAKind can be beaten by bigger FourOfAKind or 4+ PairsOfPine (variation)
  // But usually, you just follow the hierarchy.

  return false
}

const playSelected = () => {
  const selectedCards = selectedIndices.value.map(i => myHand.value[i])
  const combo = detectCombo(selectedCards)
  
  lastCombo.value = combo
  lastPlayerIndex.value = 0
  
  // Remove from hand
  players.value[0].hand = players.value[0].hand.filter((_, i) => !selectedIndices.value.includes(i))
  myHand.value = players.value[0].hand
  selectedIndices.value = []
  
  checkWin()
  if (gameState.value === 'PLAYING') nextTurn()
}

const passTurn = () => {
  selectedIndices.value = []
  nextTurn()
}

const nextTurn = () => {
  turnIndex.value = (turnIndex.value + 1) % players.value.length
  statusMessage.value = players.value[turnIndex.value].name + "'s turn"
  
  if (turnIndex.value === 0) {
    suggestMove()
  }

  if (players.value[turnIndex.value].isBot) {
    setTimeout(botPlay, 1000)
  }
}

const suggestMove = () => {
  if (!lastCombo.value || lastPlayerIndex.value === 0) return
  
  // Intelligence: Scan for defeat decks (Rule 2)
  if (lastCombo.value.type === 'Single' && lastCombo.value.cards[0].rank === '2') {
    // Find combos that can beat a single 2
    const h = [...myHand.value]
    const groups = {}
    h.forEach((c, idx) => { groups[c.rankVal] = groups[c.rankVal] || []; groups[c.rankVal].push({ ...c, originalIndex: idx }) })
    
    // Check for FourOfAKind
    for (const rVal in groups) {
      if (groups[rVal].length === 4) {
        selectedIndices.value = groups[rVal].map(c => c.originalIndex)
        statusMessage.value = "Suggestion: Defeat with Four of a Kind!"
        return
      }
    }
    
    // Check for ThreePairsOfPine
    const sortedRanks = Object.keys(groups).map(Number).sort((a,b) => a - b)
    for (let i = 0; i <= sortedRanks.length - 3; i++) {
      const slice = sortedRanks.slice(i, i + 3)
      if (slice.every((r, idx) => r === slice[0] + idx && groups[r].length >= 2 && r !== 12)) {
        const indices = []
        slice.forEach(r => indices.push(groups[r][0].originalIndex, groups[r][1].originalIndex))
        selectedIndices.value = indices
        statusMessage.value = "Suggestion: Defeat with 3 Pairs of Pine!"
        return
      }
    }
  }

  if (lastCombo.value.type === 'Pair' && lastCombo.value.cards[0].rank === '2') {
    // Similarly for Pair of 2s...
    const h = [...myHand.value]
    const groups = {}
    h.forEach((c, idx) => { groups[c.rankVal] = groups[c.rankVal] || []; groups[c.rankVal].push({ ...c, originalIndex: idx }) })
    
    for (const rVal in groups) {
      if (groups[rVal].length === 4) {
        selectedIndices.value = groups[rVal].map(c => c.originalIndex)
        statusMessage.value = "Suggestion: Defeat Pair of 2s with Four of a Kind!"
        return
      }
    }
  }
}

const botPlay = () => {
  if (gameState.value !== 'PLAYING') return
  const p = players.value[turnIndex.value]
  
  if (lastPlayerIndex.value === turnIndex.value) {
    lastCombo.value = null
  }
  
  let moveToPlay = null
  
  // Helper to find all possible combos in hand
  const findPossibleCombos = () => {
    const combos = []
    const h = [...p.hand]
    const groups = {}
    h.forEach(c => { groups[c.rankVal] = groups[c.rankVal] || []; groups[c.rankVal].push(c) })
    const sortedRanks = Object.keys(groups).map(Number).sort((a,b) => a - b)
    
    // 1. Four of a Kind
    Object.values(groups).forEach(g => { if (g.length === 4) combos.push(detectCombo(g)) })
    
    // 2. Pairs of Pine (consecutive pairs)
    for (let len = 3; len <= 8; len++) { // Tien Len uses 3, 4, 5... pairs
      for (let i = 0; i <= sortedRanks.length - len; i++) {
        const slice = sortedRanks.slice(i, i + len)
        if (slice.every((r, idx) => r === slice[0] + idx && groups[r].length >= 2 && r !== 12)) {
          const cards = []
          slice.forEach(r => cards.push(...groups[r].slice(0, 2)))
          combos.push(detectCombo(cards))
        }
      }
    }

    // 3. Straights (Sảnh) - Handle duplicates correctly
    // Get unique ranks excluding 2
    const uniqueRanks = sortedRanks.filter(r => r !== 12)
    for (let len = 3; len <= uniqueRanks.length; len++) {
      for (let i = 0; i <= uniqueRanks.length - len; i++) {
        const slice = uniqueRanks.slice(i, i + len)
        // Check if consecutive
        if (slice.every((r, idx) => r === slice[0] + idx)) {
          // For each rank in the slice, we could potentially pick any of the suits
          // For simplicity, bot picks the lowest suit for leading, or highest for beating
          // Here we just find ONE valid straight for each span
          const cards = slice.map(r => groups[r][0])
          combos.push(detectCombo(cards))
        }
      }
    }

    // 4. Triples, Pairs, Singles
    Object.values(groups).forEach(g => {
      if (g.length >= 3) combos.push(detectCombo(g.slice(0, 3)))
      if (g.length >= 2) combos.push(detectCombo(g.slice(0, 2)))
      g.forEach(c => combos.push(detectCombo([c])))
    })

    return combos
  }

  const possible = findPossibleCombos()

  if (!lastCombo.value) {
    // LEADING LOGIC
    // Is it the very first turn of the game? (Search for 3 of Diamonds)
    const isFirstTurn = players.value.every(pl => pl.hand.length === 13)
    if (isFirstTurn) {
       // Must play a combo containing 3 of Diamonds
       const leadMove = possible.find(c => c.cards.some(card => card.rank === '3' && card.suit === '♦'))
       moveToPlay = leadMove || possible.find(c => c.type === 'Single')
    } else {
       // Prefer playing the smallest single or pair to stay in control
       const singles = possible.filter(c => c.type === 'Single').sort((a,b) => a.rank - b.rank)
       const straights = possible.filter(c => c.type === 'Straight').sort((a,b) => a.length - b.length)
       moveToPlay = straights[0] || singles[0] || possible[0]
    }
  } else {
    // BEATING LOGIC
    // Try to find the smallest combo that can beat the last one
    const valid = possible.filter(c => canBeat(c, lastCombo.value))
    if (valid.length > 0) {
      // Sort by rank to use the weakest card that still wins
      valid.sort((a, b) => a.rank - b.rank || (a.suit || 0) - (b.suit || 0))
      moveToPlay = valid[0]
    }
  }
  
  if (moveToPlay) {
    lastCombo.value = moveToPlay
    lastPlayerIndex.value = turnIndex.value
    p.hand = p.hand.filter(c => !moveToPlay.cards.some(mc => mc.rank === c.rank && mc.suit === c.suit))
    statusMessage.value = `${p.name} played ${moveToPlay.type}`
  } else {
    statusMessage.value = `${p.name} passes.`
  }
  
  checkWin()
  if (gameState.value === 'PLAYING') {
    setTimeout(nextTurn, 1000)
  }
}

const checkWin = async () => {
  const winner = players.value.findIndex(p => p.hand.length === 0)
  if (winner !== -1) {
    gameState.value = 'RESOLVED'
    winnerIndex.value = winner
    
    winAmount.value = (winner === 0) ? currentBet.value : -currentBet.value
    statusMessage.value = (winner === 0) ? 'YOU WIN!' : `${players.value[winner].name} wins!`
    
    submitScore()
  }
}

const submitScore = async () => {
  try {
    const res = await apiPost('/games/scores/submit', { 
      game_type: 'bigtwo', 
      score: winAmount.value,
      metadata: { 
        bet: currentBet.value,
        difficulty: 'MEDIUM' 
      }
    })
    console.log(`%c💰 BigTwo: Score submitted. Reward: ${winAmount.value}. New Chips: ${res.new_chips}`, 'color: #10b981; font-weight: bold')
    
    if (res.new_chips !== undefined) {
      if (!profile.value) profile.value = {}
      profile.value.chip_balance = res.new_chips
    } else {
      loadProfile()
    }
  } catch (err) {
    console.error('Score submission error:', err)
  }
}

onMounted(() => {
  loadProfile()
  players.value.push({ name: 'You', isBot: false, hand: [] })
})
</script>

<style scoped>
.bigtwo-game {
  width: 100%;
  height: 100%;
  padding: 2rem;
  background: radial-gradient(circle at center, rgba(44, 62, 80, 0.9) 0%, rgba(0, 0, 0, 0.95) 100%);
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.lobby-view {
  max-width: 800px;
  width: 90%;
  margin: auto;
  padding: 3rem;
  text-align: center;
  border-radius: 20px;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  box-shadow: var(--glass-shadow);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
}

.lobby-view h2 {
  font-size: 2rem;
  margin-bottom: 2rem;
  background: linear-gradient(135deg, #ffd700, #ff8c00);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 900;
}

.players-list {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-bottom: 2rem;
  width: 100%;
}

.player-slot {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.player-slot.is-me {
  border-color: #ffd700;
  background: rgba(255, 215, 0, 0.1);
}

.player-slot .avatar {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.player-slot .name {
  font-weight: 700;
  font-size: 0.9rem;
}

.lobby-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.primary-actions {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  width: 100%;
}

.start-btn { 
  background: linear-gradient(135deg, #ffd700, #ff8c00);
  color: #000;
  font-size: 1.1rem;
}

.single-player-btn { 
  background: rgba(59, 130, 246, 0.2); 
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.5);
  margin-left: 0;
}

.add-bot-btn.highlight { 
  background: transparent;
  border: 2px dashed rgba(255, 215, 0, 0.3);
  color: #ffd700;
  margin-top: 0;
}

.add-bot-btn:hover {
  background: rgba(255, 215, 0, 0.1);
  border-style: solid;
}

.room-info {
  margin-bottom: 1rem;
  font-family: 'Courier New', Courier, monospace;
}

.game-header-stats { display: flex; width: 100%; justify-content: space-between; padding: 1rem; }
.stat .value { font-size: 1.2rem; font-weight: 800; color: #ffd700; }
.status-msg { font-style: italic; color: #aaa; }

.start-btn, .add-bot-btn, .single-player-btn {
  padding: 1rem 2rem;
  border-radius: 8px;
  font-weight: 800;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.room-id { color: #ffd700; font-weight: 900; margin-left: 0.5rem; }

.primary-actions {
  display: flex;
  justify-content: center;
}

.table-view { flex: 1; width: 100%; position: relative; display: flex; flex-direction: column; }

.opponents-layer { position: absolute; width: 100%; height: 100%; pointer-events: none; }
.opponent-slot { position: absolute; text-align: center; transition: all 0.3s; padding: 0.5rem; border-radius: 12px; }
.active-turn { 
  background: rgba(255, 215, 0, 0.1);
  box-shadow: 0 0 20px rgba(255, 215, 0, 0.2);
  animation: pulse-glow 2s infinite;
  z-index: 10;
}

@keyframes pulse-glow {
  0% { box-shadow: 0 0 5px rgba(255, 215, 0, 0.2); border: 1px solid rgba(255, 215, 0, 0.3); }
  50% { box-shadow: 0 0 20px rgba(255, 215, 0, 0.5); border: 1px solid rgba(255, 215, 0, 0.8); }
  100% { box-shadow: 0 0 5px rgba(255, 215, 0, 0.2); border: 1px solid rgba(255, 215, 0, 0.3); }
}

.turn-pointer {
  position: absolute;
  top: -25px;
  left: 50%;
  transform: translateX(-50%);
  color: #ffd700;
  font-size: 1.5rem;
  filter: drop-shadow(0 0 5px rgba(255, 215, 0, 0.8));
  animation: bounce 1s infinite;
}

@keyframes bounce {
  0%, 100% { transform: translate(-50%, 0); }
  50% { transform: translate(-50%, -5px); }
}

.opp-0 { top: 10%; left: 10%; }
.opp-1 { top: 0; left: 45%; }
.opp-2 { top: 10%; right: 10%; }

.cards-back { display: flex; gap: 4px; justify-content: center; margin-top: 5px; }
.card-back { width: 30px; height: 45px; background: #c0392b; border: 1px solid white; border-radius: 4px; }

.last-played-area { flex: 1; display: flex; align-items: center; justify-content: center; }
.last-combo { padding: 1.5rem; text-align: center; min-width: 200px; }
.played-by { font-size: 0.82rem; color: #60a5fa; margin-bottom: 0.8rem; font-weight: 600; }
.combo-type { margin-top: 0.8rem; font-weight: 900; color: #ffd700; text-transform: uppercase; letter-spacing: 1px; }

.cards-hand.collated {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: -30px; /* Base overlap */
  padding: 1rem;
}

.card.mini.layered {
  width: 50px;
  height: 75px;
  font-size: 1.2rem;
  margin-right: -30px;
  transform: rotate(calc((var(--index) - 1.5) * 5deg));
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  box-shadow: -2px 0 5px rgba(0,0,0,0.3);
  background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%);
}

.card.mini.layered:last-child {
  margin-right: 0;
}

.card.mini.layered:hover {
  transform: translateY(-10px) scale(1.1);
  z-index: 100 !important;
  box-shadow: 0 5px 15px rgba(0,0,0,0.4);
}

.card-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.card-content .rank {
  font-size: 1.4rem;
  margin-bottom: -2px;
}

.card-content .suit {
  font-size: 1rem;
}

.my-hand-container {
  display: flex;
  justify-content: center;
  gap: -20px; /* Overlap cards */
  padding: 2rem;
  overflow-x: auto;
  width: 100%;
}

.card {
  width: 80px;
  height: 120px;
  background: white;
  color: black;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  font-weight: 900;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 8px rgba(0,0,0,0.5);
  margin-right: -20px;
  user-select: none;
}

.card:hover { transform: translateY(-15px); z-index: 10; }
.card.selected { transform: translateY(-30px); border: 3px solid #ffd700; z-index: 10; }

.card.hearts, .card.diamonds { color: #d12d36; }

.player-actions { display: flex; gap: 1rem; justify-content: center; margin-top: 1rem; }
.play-btn { background: #10b981; color: white; border: none; padding: 0.8rem 2rem; border-radius: 8px; font-weight: 800; cursor: pointer; }
.pass-btn { background: #64748b; color: white; border: none; padding: 0.8rem 2rem; border-radius: 8px; font-weight: 800; cursor: pointer; }

.result-overlay { position: absolute; top: 30%; padding: 4rem; text-align: center; z-index: 100; }

.mini { width: 40px; height: 60px; font-size: 1rem; margin-right: 2px; }

.reward { font-size: 1.5rem; font-weight: 800; color: #ffd700; margin-bottom: 1.5rem; }
.reward.loss { color: #ef4444; }

.betting-overlay {
  padding: 3rem;
  width: 100%;
  display: flex;
  justify-content: center;
  z-index: 20;
}
</style>
