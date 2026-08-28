#!/usr/bin/env python3
"""
Master Orchestrator for Daily Game Studio Devlog Video Pipeline
Complete end-to-end pipeline: Scripts → Assets → Render → Upload
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any
import argparse
import time

GAMES_DIR = Path("/home/ethan/Hermes Project/daily-games")
PIPELINE_DIR = GAMES_DIR / "video-pipeline"
SCRIPTS_DIR = PIPELINE_DIR / "scripts"
OUTPUT_DIR = PIPELINE_DIR / "output"

class PipelineOrchestrator:
    def __init__(self, start_ep: int = 1, end_ep: int = 54, engine: str = "moviepy"):
        self.start_ep = start_ep
        self.end_ep = end_ep
        self.engine = engine
        self.results = {
            "scripts": [],
            "assets": [],
            "render": [],
            "upload": []
        }
    
    def run_cmd(self, cmd: List[str], description: str, timeout: int = 300) -> bool:
        """Run a command and track results"""
        print(f"\n{'='*60}")
        print(f"🔧 {description}")
        print(f"{'='*60}")
        print(f"Command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        
        if result.returncode == 0:
            print(f"✓ {description} completed")
            if result.stdout:
                # Show last few lines
                lines = result.stdout.strip().split('\n')
                for line in lines[-5:]:
                    print(f"   {line}")
            return True
        else:
            print(f"✗ {description} failed:")
            if result.stderr:
                lines = result.stderr.strip().split('\n')
                for line in lines[-10:]:
                    print(f"   {line}")
            return False
    
    def generate_scripts(self) -> bool:
        """Generate scripts for all episodes"""
        cmd = [sys.executable, str(SCRIPTS_DIR / "script_generator.py"), "--all"]
        success = self.run_cmd(cmd, "Generating scripts for all 54 episodes")
        if success:
            self.results["scripts"] = list(range(self.start_ep, self.end_ep + 1))
        return success
    
    def generate_assets(self, ep_num: int) -> bool:
        """Generate assets for one episode"""
        cmd = [sys.executable, str(SCRIPTS_DIR / "generate_assets.py"), "--episode", str(ep_num)]
        success = self.run_cmd(cmd, f"Generating assets for Episode #{ep_num:02d}", timeout=600)
        if success:
            self.results["assets"].append(ep_num)
        return success
    
    def render_episode(self, ep_num: int) -> bool:
        """Render one episode"""
        cmd = [
            sys.executable, str(SCRIPTS_DIR / "render_episode.py"),
            "--episode", str(ep_num), "--engine", self.engine
        ]
        success = self.run_cmd(cmd, f"Rendering Episode #{ep_num:02d}", timeout=600)
        if success:
            self.results["render"].append(ep_num)
        return success
    
    def upload_episode(self, ep_num: int) -> bool:
        """Upload one episode to YouTube"""
        cmd = [sys.executable, str(SCRIPTS_DIR / "upload_youtube.py"), "--episode", str(ep_num)]
        success = self.run_cmd(cmd, f"Uploading Episode #{ep_num:02d} to YouTube", timeout=600)
        if success:
            self.results["upload"].append(ep_num)
        return success
    
    def run_full_pipeline(self, skip_upload: bool = False) -> Dict[str, Any]:
        """Run the complete pipeline for all episodes"""
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║     Daily Game Studio Devlog - Video Pipeline Orchestrator    ║
║                                                              ║
║  Episodes: {self.start_ep:02d} - {self.end_ep:02d}                                        ║
║  Engine: {self.engine}                                      ║
║  Upload: {'Enabled' if not skip_upload else 'Disabled'}                                            ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        start_time = time.time()
        
        # Step 1: Generate all scripts
        if not self.generate_scripts():
            print("❌ Script generation failed, aborting pipeline")
            return self.results
        
        # Step 2-4: Process each episode
        for ep_num in range(self.start_ep, self.end_ep + 1):
            print(f"\n{'#'*60}")
            print(f"# PROCESSING EPISODE #{ep_num:02d}")
            print(f"{'#'*60}")
            
            # Generate assets
            if not self.generate_assets(ep_num):
                print(f"⚠️  Episode {ep_num} asset generation failed, skipping...")
                continue
            
            # Render
            if not self.render_episode(ep_num):
                print(f"⚠️  Episode {ep_num} rendering failed, skipping...")
                continue
            
            # Upload (optional)
            if not skip_upload:
                if not self.upload_episode(ep_num):
                    print(f"⚠️  Episode {ep_num} upload failed, continuing...")
                    # Don't break on upload failure
            
            # Small delay between episodes
            time.sleep(2)
        
        elapsed = time.time() - start_time
        self._print_summary(elapsed)
        self._save_results()
        
        return self.results
    
    def _print_summary(self, elapsed: float):
        """Print pipeline summary"""
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    PIPELINE SUMMARY                           ║
╠══════════════════════════════════════════════════════════════╣
║  Total time: {elapsed/60:.1f} minutes                                  ║
║  Episodes processed: {self.end_ep - self.start_ep + 1}                                     ║
║                                                              ║
║  Scripts generated:    {len(self.results['scripts']):2d} / {self.end_ep - self.start_ep + 1:2d}                                ║
║  Assets generated:     {len(self.results['assets']):2d} / {self.end_ep - self.start_ep + 1:2d}                                ║
║  Episodes rendered:    {len(self.results['render']):2d} / {self.end_ep - self.start_ep + 1:2d}                                ║
║  Episodes uploaded:    {len(self.results['upload']):2d} / {self.end_ep - self.start_ep + 1:2d}                                ║
╚══════════════════════════════════════════════════════════════╝
        """)
    
    def _save_results(self):
        """Save pipeline results"""
        results_file = OUTPUT_DIR / "pipeline_results.json"
        results_file.write_text(json.dumps({
            "timestamp": time.time(),
            "start_episode": self.start_ep,
            "end_episode": self.end_ep,
            "engine": self.engine,
            "results": self.results
        }, indent=2))
        print(f"📄 Results saved: {results_file}")

def main():
    parser = argparse.ArgumentParser(description="Daily Game Studio Devlog - Full Pipeline Orchestrator")
    parser.add_argument("--start", type=int, default=1, help="Start episode")
    parser.add_argument("--end", type=int, default=54, help="End episode")
    parser.add_argument("--engine", choices=["moviepy", "ffmpeg"], default="moviepy", help="Rendering engine")
    parser.add_argument("--skip-upload", action="store_true", help="Skip YouTube upload")
    parser.add_argument("--scripts-only", action="store_true", help="Only generate scripts")
    parser.add_argument("--assets-only", action="store_true", help="Only generate assets (needs scripts)")
    parser.add_argument("--render-only", action="store_true", help="Only render (needs assets)")
    parser.add_argument("--upload-only", action="store_true", help="Only upload (needs rendered videos)")
    args = parser.parse_args()
    
    orchestrator = PipelineOrchestrator(args.start, args.end, args.engine)
    
    if args.scripts_only:
        orchestrator.generate_scripts()
    elif args.assets_only:
        for ep in range(args.start, args.end + 1):
            orchestrator.generate_assets(ep)
    elif args.render_only:
        for ep in range(args.start, args.end + 1):
            orchestrator.render_episode(ep)
    elif args.upload_only:
        for ep in range(args.start, args.end + 1):
            orchestrator.upload_episode(ep)
    else:
        orchestrator.run_full_pipeline(skip_upload=args.skip_upload)

if __name__ == "__main__":
    main()