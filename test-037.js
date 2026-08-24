const { GameTester } = require('./test-runner.js');
const tester = new GameTester();
tester.testGame('game-037', 'games/game-037')
  .then(result => {
    console.log('game-037 result:', JSON.stringify(result, null, 2));
    process.exit(result.passed ? 0 : 1);
  })
  .catch(err => {
    console.error('Error:', err);
    process.exit(1);
  });
