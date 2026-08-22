#!/usr/bin/env node

const { GameTester } = require('./test-runner');
const { AutoFixer } = require('./auto-fixer');
const { callNIMAPI } = require('./nim-api-wrapper');
const fs = require('fs');
const path = require('path');

class SelfHealingLoop {
    constructor() {
        this.tester = new GameTester();
        this.fixer = new AutoFixer();
        this.maxRetries = 3;
        this.cycleCount = 0;
    }

    async run() {
        console.log('🚀 Starting Self-Healing Loop');
        console.log('==============================\n');
        
        while (true) {
            this.cycleCount++;
            console.log(`\n🔄 Cycle ${this.cycleCount} started at ${new Date().toISOString()}`);
            
            try {
                // 1. Run tests on all games
                const results = await this.tester.runAllTests();
                const report = this.tester.generateReport();
                
                console.log('\n📊 Test Summary:');
                console.log(`  Total Games: ${report.totalGames}`);
                console.log(`  Passed: ${report.passedGames}`);
                console.log(`  Failed: ${report.failedGames}`);
                console.log(`  Total Bugs: ${report.totalBugs} (Critical: ${report.criticalBugs}, Major: ${report.majorBugs}, Minor: ${report.minorBugs})`);
                
                // Save report
                this.saveReport(report);
                
                // 2. If no bugs, wait and continue
                if (report.totalBugs === 0) {
                    console.log('\n✅ All games healthy! Waiting for next cycle...');
                    await this.sleep(3600000); // 1 hour
                    continue;
                }
                
                // 3. Fix bugs game by game
                for (const result of this.tester.results) {
                    if (result.bugs.length > 0) {
                        await this.fixGameWithRetry(result.gameId, result.gamePath, result.bugs);
                    }
                }
                
                // 4. Verify fixes
                console.log('\n🔍 Verifying fixes...');
                const verifyResults = await this.tester.runAllTests();
                const verifyReport = this.tester.generateReport();
                
                console.log('\n✅ Verification Summary:');
                console.log(`  Total Bugs: ${verifyReport.totalBugs} (was ${this.tester.generateReport().totalBugs})`);
                
                if (verifyReport.totalBugs === 0) {
                    console.log('\n🎉 All bugs fixed!');
                } else {
                    console.log(`\n⚠️ ${verifyReport.totalBugs} bugs remain, will retry next cycle`);
                }
                
            } catch (error) {
                console.error('❌ Cycle error:', error);
            }
            
            // Wait before next cycle (1 hour)
            console.log('\n⏳ Waiting 1 hour before next cycle...');
            await this.sleep(3600000);
        }
    }
    
    async fixGameWithRetry(gameId, gamePath, bugs) {
        // Sort bugs by severity
        const sortedBugs = [...bugs].sort((a, b) => {
            const severityOrder = { CRITICAL: 3, MAJOR: 2, MINOR: 1 };
            return severityOrder[b.severity] - severityOrder[a.severity];
        });
        
        for (let attempt = 1; attempt <= this.maxRetries; attempt++) {
            console.log(`\n🔧 Fixing ${gameId} (attempt ${attempt}/${this.maxRetries})`);
            
            const result = await this.fixer.fixGame(gameId, gamePath, bugs);
            
            if (result.success) {
                // Test the fix
                const testResult = await this.tester.testGame(gameId, gamePath);
                
                if (testResult.passed) {
                    console.log(`✅ ${gameId} fixed and verified!`);
                    return true;
                } else {
                    console.log(`⚠️ Fix applied but ${gameId} still has ${testResult.bugs.length} bugs`);
                }
            }
            
            if (attempt < 3) {
                console.log(`⏳ Waiting 30 seconds before retry...`);
                await this.sleep(30000);
            }
        }
        
        console.log(`❌ Failed to fix ${gameId} after ${this.maxRetries} attempts`);
        return false;
    }
    
    saveReport(report) {
        const reportDir = path.join('/home/ethan/Hermes Project/daily-games', 'reports');
        if (!fs.existsSync(reportDir)) {
            fs.mkdirSync(reportDir, { recursive: true });
        }
        
        const filename = `report-${new Date().toISOString().replace(/[:.]/g, '-')}.json`;
        fs.writeFileSync(
            path.join(reportDir, filename),
            JSON.stringify(report, null, 2)
        );
    }
    
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Run if executed directly
if (require.main === module) {
    const loop = new SelfHealingLoop();
    loop.run().catch(console.error);
}

module.exports = { SelfHealingLoop };