"""
Video Compression Module
Handles video compression with hardware acceleration for social media platforms
Enhanced with dynamic optimization for maximum quality within size constraints
"""

import os
import subprocess
import shutil
import math
from typing import Dict, Any, Optional, Tuple, List
import logging
from pathlib import Path
from tqdm import tqdm
import json

from .hardware_detector import HardwareDetector
from .config_manager import ConfigManager
from .advanced_optimizer import AdvancedVideoOptimizer
from .performance_enhancer import PerformanceEnhancer
from .ffmpeg_utils import FFmpegUtils
from .video_segmenter import VideoSegmenter

logger = logging.getLogger(__name__)

class GracefulCancellation(Exception):
    """Raised to indicate a user-requested shutdown/cancellation."""
    pass


class DynamicVideoCompressor:
    def __init__(self, config_manager: ConfigManager, hardware_detector: HardwareDetector):
        self.config = config_manager
        self.hardware = hardware_detector
        self.temp_dir = self.config.get_temp_dir()
        
        # Performance enhancement
        self.performance_enhancer = PerformanceEnhancer(config_manager)
        
        # Shutdown handling
        self.shutdown_requested = False
        self.current_ffmpeg_process = None
        
        # Statistics
        self.stats = {
            'total_compressions': 0,
            'successful_compressions': 0,
            'failed_compressions': 0,
            'hardware_fallbacks': 0,
            'average_compression_time': 0,
            'total_processing_time': 0
        }
        
        # Initialize advanced components
        self.advanced_optimizer = AdvancedVideoOptimizer(config_manager, hardware_detector)
        self.video_segmenter = VideoSegmenter(config_manager, hardware_detector)
        
        # Optimize system resources
        self.system_optimizations = self.performance_enhancer.optimize_system_resources()
        
    def compress_video(self, input_path: str, output_path: str, platform: str = None, 
                      max_size_mb: int = None, use_advanced_optimization: bool = True) -> Dict[str, Any]:
        """
        Compress video with dynamic optimization for maximum quality within size constraints
        Enhanced with advanced optimization techniques and performance improvements
        """
        
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input video file not found: {input_path}")
        
        logger.info(f"Starting enhanced video compression: {input_path} -> {output_path}")
        
        # Get platform configuration
        platform_config = {}
        if platform:
            platform_config = self.config.get_platform_config(platform, 'video_compression')
            logger.info(f"Using platform configuration for: {platform}")
        
        # Determine target file size
        target_size_mb = max_size_mb or platform_config.get('max_file_size_mb') or self.config.get('video_compression.max_file_size_mb', 10)
        
        # Check cache for similar operations
        @self.performance_enhancer.cached_operation(ttl_hours=6)
        def cached_analysis(file_path, file_size, target_size):
            return self._analyze_video_content(file_path)
        
        # Early-cancel before analysis if shutdown requested
        if self.shutdown_requested:
            return {'success': False, 'cancelled': True}

        # Get comprehensive video analysis (cached), but handle graceful cancellation
        file_size = os.path.getsize(input_path)
        try:
            video_info = cached_analysis(input_path, file_size, target_size_mb)
        except GracefulCancellation:
            return {'success': False, 'cancelled': True}
        original_size_mb = file_size / (1024 * 1024)
        
        logger.info(f"Original video: {video_info['width']}x{video_info['height']}, "
                   f"{video_info['duration']:.2f}s, {original_size_mb:.2f}MB, "
                   f"complexity: {video_info['complexity_score']:.2f}")
        
        # Check if video should be segmented instead of compressed as single file
        logger.info(f"Checking video segmentation: original size {original_size_mb:.1f}MB, target {target_size_mb}MB")
        logger.info(f"Video info keys: {list(video_info.keys())}")
        logger.info(f"Video info size_bytes: {video_info.get('size_bytes', 'NOT FOUND')}")
        
        if self.video_segmenter.should_segment_video(video_info['duration'], video_info, target_size_mb):
            logger.info("Video will be segmented instead of compressed as single file")
            return self._compress_with_segmentation(
                input_path, output_path, target_size_mb, platform_config, video_info, platform
            )
        
        # If already under target size and no platform specified, just copy
        if original_size_mb <= target_size_mb and not platform:
            shutil.copy2(input_path, output_path)
            logger.info("Video already meets size requirements, copied without compression")
            return self._get_compression_results(input_path, output_path, video_info, "copy")
        
        # Choose optimization strategy based on file size and system resources
        if use_advanced_optimization and (original_size_mb > 50 or target_size_mb < 5):
            logger.info("Using advanced optimization for challenging compression requirements")
            return self._compress_with_advanced_optimization(
                input_path, output_path, target_size_mb, platform_config, video_info
            )
        
        # Use adaptive quality processing for medium complexity files
        elif original_size_mb > 20:
            logger.info("Using adaptive quality processing for medium complexity file")
            return self._compress_with_adaptive_quality(
                input_path, output_path, target_size_mb, platform_config, video_info
            )
        
        # Use standard dynamic optimization for simpler cases
        else:
            return self._compress_with_standard_optimization(
                input_path, output_path, target_size_mb, platform_config, video_info
            )
    
    def _compress_with_advanced_optimization(self, input_path: str, output_path: str,
                                           target_size_mb: float, platform_config: Dict[str, Any],
                                           video_info: Dict[str, Any]) -> Dict[str, Any]:
        """Use advanced optimization techniques for challenging compression"""
        
        try:
            # Use the advanced optimizer
            result = self.advanced_optimizer.optimize_with_advanced_techniques(
                input_path, output_path, target_size_mb, platform_config
            )
            
            # Convert result format to match expected output
            compressed_size_mb = result['size_mb']
            return {
                'success': True,  # Add success flag
                'input_file': input_path,
                'output_file': output_path,
                'method': 'advanced_optimized',
                'original_size_mb': os.path.getsize(input_path) / (1024 * 1024),
                'compressed_size_mb': compressed_size_mb,
                'size_mb': compressed_size_mb,  # Add alias for automated workflow
                'compression_ratio': ((os.path.getsize(input_path) - os.path.getsize(output_path)) / os.path.getsize(input_path)) * 100,
                'space_saved_mb': (os.path.getsize(input_path) - os.path.getsize(output_path)) / (1024 * 1024),
                'video_info': video_info,
                'optimization_strategy': result.get('candidate_name', 'advanced'),
                'quality_score': result.get('quality_score', 8.0),
                'attempts_made': 1,
                'encoder_used': result.get('candidate_data', {}).get('encoder', 'unknown')
            }
            
        except Exception as e:
            logger.warning(f"Advanced optimization failed, falling back to standard: {e}")
            return self._compress_with_standard_optimization(
                input_path, output_path, target_size_mb, platform_config, video_info
            )
    
    def _compress_with_adaptive_quality(self, input_path: str, output_path: str,
                                      target_size_mb: float, platform_config: Dict[str, Any],
                                      video_info: Dict[str, Any]) -> Dict[str, Any]:
        """Use adaptive quality processing for optimal results"""
        
        try:
            # Use performance enhancer's adaptive processing
            quality_levels = ['fast', 'balanced', 'high_quality']
            
            # Create a processing function that uses our compression logic
            def process_quality_level(task):
                quality_level = task['quality_level']
                temp_output = task['temp_output']
                
                # Map quality levels to compression parameters
                quality_params = {
                    'fast': {'crf': 28, 'preset': 'veryfast', 'priority': 'speed'},
                    'balanced': {'crf': 23, 'preset': 'medium', 'priority': 'balanced'},
                    'high_quality': {'crf': 18, 'preset': 'slow', 'priority': 'quality'}
                }
                
                params = quality_params[quality_level]
                
                # Use our compression logic with these parameters
                compression_params = self._calculate_compression_params_with_quality(
                    video_info, platform_config, target_size_mb, params
                )
                
                # Build and execute FFmpeg command
                ffmpeg_cmd = self._build_ffmpeg_command(input_path, temp_output, compression_params, 1)
                self._execute_ffmpeg_with_progress(ffmpeg_cmd, video_info['duration'])
                
                # Calculate result quality
                if os.path.exists(temp_output):
                    file_size_mb = os.path.getsize(temp_output) / (1024 * 1024)
                    quality_score = self._calculate_quality_score(compression_params, video_info)
                    
                    return {
                        'quality_level': quality_level,
                        'output_path': temp_output,
                        'size_mb': file_size_mb,
                        'quality_score': quality_score,
                        'settings': params,
                        'processing_time': 1.0,  # Placeholder
                        'success': file_size_mb <= target_size_mb
                    }
                
                return None
            
            # Use adaptive quality processing
            best_result = self.performance_enhancer.adaptive_quality_processing(
                input_path, target_size_mb, quality_levels
            )
            
            # Move result to final output
            if best_result and os.path.exists(best_result.get('output_path', '')):
                shutil.move(best_result['output_path'], output_path)
                
                return {
                    'input_file': input_path,
                    'output_file': output_path,
                    'method': 'adaptive_quality',
                    'original_size_mb': os.path.getsize(input_path) / (1024 * 1024),
                    'compressed_size_mb': best_result.get('size_mb', 0),
                    'compression_ratio': ((os.path.getsize(input_path) - os.path.getsize(output_path)) / os.path.getsize(input_path)) * 100,
                    'space_saved_mb': (os.path.getsize(input_path) - os.path.getsize(output_path)) / (1024 * 1024),
                    'video_info': video_info,
                    'optimization_strategy': f"adaptive_{best_result.get('quality_level', 'balanced')}",
                    'quality_score': best_result.get('quality_score', 7.0),
                    'attempts_made': len(quality_levels),
                    'encoder_used': self.hardware.get_best_encoder("h264")[0]
                }
            
        except Exception as e:
            logger.warning(f"Adaptive quality processing failed, falling back to standard: {e}")
        
        # Fallback to standard optimization
        return self._compress_with_standard_optimization(
            input_path, output_path, target_size_mb, platform_config, video_info
        )
    
    def _compress_with_standard_optimization(self, input_path: str, output_path: str,
                                           target_size_mb: float, platform_config: Dict[str, Any],
                                           video_info: Dict[str, Any]) -> Dict[str, Any]:
        """Use standard dynamic optimization (original implementation)"""
        
        # This is the original dynamic optimization logic
        best_result = None
        compression_attempts = []
        
        try:
            # Strategy 1: Content-aware optimal compression
            logger.info("Attempting Strategy 1: Content-aware optimal compression")
            result = self._compress_with_content_awareness(
                input_path, video_info, platform_config, target_size_mb
            )
            if result:
                compression_attempts.append(result)
                if result['size_mb'] <= target_size_mb:
                    best_result = result
                    logger.info(f"Strategy 1 successful: {result['size_mb']:.2f}MB")
            
            # Strategy 2: Two-pass encoding if Strategy 1 didn't work perfectly
            if not best_result or result['size_mb'] > target_size_mb * 0.95:
                logger.info("Attempting Strategy 2: Two-pass precision encoding")
                result = self._compress_with_two_pass(
                    input_path, video_info, platform_config, target_size_mb, best_result
                )
                if result:
                    compression_attempts.append(result)
                    if result['size_mb'] <= target_size_mb:
                        if not best_result or result['quality_score'] > best_result.get('quality_score', 0):
                            best_result = result
                            logger.info(f"Strategy 2 improved result: {result['size_mb']:.2f}MB")
            
            # Strategy 3: Adaptive resolution and quality optimization
            if not best_result:
                logger.info("Attempting Strategy 3: Adaptive resolution optimization")
                result = self._compress_with_adaptive_resolution(
                    input_path, video_info, platform_config, target_size_mb
                )
                if result:
                    compression_attempts.append(result)
                    if result['size_mb'] <= target_size_mb:
                        best_result = result
                        logger.info(f"Strategy 3 successful: {result['size_mb']:.2f}MB")
            
            # Strategy 4: Aggressive optimization as last resort
            if not best_result:
                logger.info("Attempting Strategy 4: Aggressive optimization (last resort)")
                result = self._compress_with_aggressive_optimization(
                    input_path, video_info, platform_config, target_size_mb
                )
                if result:
                    compression_attempts.append(result)
                    if result['size_mb'] <= target_size_mb:
                        best_result = result
                        logger.info(f"Strategy 4 successful: {result['size_mb']:.2f}MB")
            
            if not best_result:
                raise RuntimeError(f"Failed to compress video under {target_size_mb}MB with all optimization strategies")
            
            # Move best result to final output
            shutil.move(best_result['temp_file'], output_path)
            
            # Clean up other attempts
            for attempt in compression_attempts:
                if attempt != best_result and os.path.exists(attempt['temp_file']):
                    os.remove(attempt['temp_file'])
            
            # Generate final results
            results = self._get_compression_results(input_path, output_path, video_info, "dynamic_optimized")
            results['optimization_strategy'] = best_result['strategy']
            results['quality_score'] = best_result.get('quality_score', 0)
            results['attempts_made'] = len(compression_attempts)
            
            logger.info(f"Dynamic compression completed: {results.get('compression_ratio', 0):.1f}% reduction, "
                       f"strategy: {best_result.get('strategy', 'unknown')}")

            # Note: Do not create folder.jpg for single MP4 outputs; reserved for segmented outputs only
            
            return results
            
        except Exception as e:
            # Clean up any temporary files
            for attempt in compression_attempts:
                if os.path.exists(attempt['temp_file']):
                    os.remove(attempt['temp_file'])
            raise
    
    def _analyze_video_content(self, video_path: str) -> Dict[str, Any]:
        """Analyze video content for intelligent compression decisions"""
        try:
            # Respect shutdown requests: abort analysis without noisy errors
            if self.shutdown_requested:
                raise GracefulCancellation()
            # Get basic video info
            # Lightweight ffprobe: avoid frame-level enumeration which is slow on long videos
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams',
                video_path
            ]
            
            # Increase timeout for large files to prevent premature timeouts
            try:
                file_size_mb_for_timeout = os.path.getsize(video_path) / (1024 * 1024)
            except Exception:
                file_size_mb_for_timeout = 0
            probe_timeout = 60
            if file_size_mb_for_timeout > 1000:
                probe_timeout = 240
            elif file_size_mb_for_timeout > 300:
                probe_timeout = 120

            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=probe_timeout
            )
            
            if result.returncode != 0:
                # If shutdown occurred during probe, treat as graceful cancel
                if self.shutdown_requested:
                    raise GracefulCancellation()
                raise subprocess.CalledProcessError(result.returncode, cmd, result.stderr)
            
            stdout_text = result.stdout or ""
            probe_data = json.loads(stdout_text) if stdout_text.strip() else {}
            
            # Find video stream
            video_stream = next(
                (stream for stream in probe_data['streams'] if stream['codec_type'] == 'video'),
                None
            )
            
            if not video_stream:
                raise ValueError("No video stream found in file")
            
            # Basic video properties
            width = int(video_stream.get('width', 0))
            height = int(video_stream.get('height', 0))
            duration = float(probe_data['format'].get('duration', 0))
            bitrate = int(probe_data['format'].get('bit_rate', 0))
            fps = FFmpegUtils.parse_fps(video_stream.get('r_frame_rate', '30/1'))
            
            # Content complexity analysis
            complexity_score = self._calculate_content_complexity(probe_data, width, height, duration)
            
            # Motion analysis
            motion_level = self._estimate_motion_level(video_stream, duration)
            
            # Scene change detection
            scene_changes = self._estimate_scene_changes(duration, fps)
            
            return {
                'width': width,
                'height': height,
                'duration': duration,
                'bitrate': bitrate,
                'fps': fps,
                'codec': video_stream.get('codec_name', 'unknown'),
                'size_bytes': int(probe_data['format'].get('size', 0)),
                'complexity_score': complexity_score,
                'motion_level': motion_level,
                'scene_changes': scene_changes,
                'aspect_ratio': width / height if height > 0 else 1.0,
                'pixel_count': width * height,
                'bitrate_per_pixel': bitrate / (width * height) if (width * height) > 0 else 0
            }
            
        except GracefulCancellation:
            # Propagate cancellation to caller to avoid further work/log noise
            raise
        except subprocess.TimeoutExpired as e:
            # Gracefully degrade on timeout for massive videos
            logger.warning(f"ffprobe analysis timed out after {getattr(e, 'timeout', 'unknown')}s; using basic video info")
            return self._get_basic_video_info(video_path)
        except Exception as e:
            if self.shutdown_requested:
                # Avoid alarming error logs on shutdown; return minimal info to allow fast exit
                logger.info("Video analysis aborted due to shutdown request")
                raise GracefulCancellation()
            else:
                logger.warning(f"Failed to analyze video content quickly; using basic info: {e}")
                # Fallback to basic analysis
                return self._get_basic_video_info(video_path)
    
    def _calculate_content_complexity(self, probe_data: Dict, width: int, height: int, duration: float) -> float:
        """Calculate content complexity score (0-10, higher = more complex)"""
        try:
            # Base complexity from resolution and duration
            pixel_complexity = math.log10(width * height) / 6.0 * 10  # Normalize to 0-10
            
            # Estimate complexity from bitrate if available
            format_info = probe_data.get('format', {})
            bitrate = int(format_info.get('bit_rate', 0))
            
            if bitrate > 0:
                # Expected bitrate for resolution
                expected_bitrate = (width * height * 30 * 0.1)  # Rough estimate
                bitrate_complexity = min(bitrate / expected_bitrate * 3, 10)
            else:
                bitrate_complexity = 5  # Default medium complexity
            
            # Combine factors
            complexity = (pixel_complexity * 0.4 + bitrate_complexity * 0.6)
            return max(0, min(10, complexity))
            
        except Exception:
            return 5.0  # Default medium complexity
    
    def _estimate_motion_level(self, video_stream: Dict, duration: float) -> str:
        """Estimate motion level in video"""
        # This is a simplified estimation - in reality you'd analyze actual frames
        fps = FFmpegUtils.parse_fps(video_stream.get('r_frame_rate', '30/1'))
        
        if fps >= 50:
            return "high"
        elif fps >= 30:
            return "medium"
        else:
            return "low"
    
    def _estimate_scene_changes(self, duration: float, fps: float) -> int:
        """Estimate number of scene changes"""
        # Rough estimate: average video has a scene change every 3-5 seconds
        return max(1, int(duration / 4))
    
    def _compress_with_content_awareness(self, input_path: str, video_info: Dict[str, Any], 
                                       platform_config: Dict[str, Any], target_size_mb: float) -> Optional[Dict[str, Any]]:
        """Content-aware compression strategy"""
        try:
            temp_output = os.path.join(self.temp_dir, "content_aware_output.mp4")
            
            # Calculate optimal parameters based on content analysis
            params = self._calculate_intelligent_params(video_info, platform_config, target_size_mb)
            
            # Build and execute FFmpeg command
            ffmpeg_cmd = self._build_intelligent_ffmpeg_command(input_path, temp_output, params)
            self._execute_ffmpeg_with_progress(ffmpeg_cmd, video_info['duration'])
            
            if os.path.exists(temp_output):
                size_mb = os.path.getsize(temp_output) / (1024 * 1024)
                quality_score = self._calculate_quality_score(params, video_info)
                
                return {
                    'temp_file': temp_output,
                    'size_mb': size_mb,
                    'strategy': 'content_aware',
                    'quality_score': quality_score,
                    'params': params
                }
            
        except Exception as e:
            logger.warning(f"Content-aware compression failed: {e}")
            return None
    
    def _compress_with_two_pass(self, input_path: str, video_info: Dict[str, Any], 
                              platform_config: Dict[str, Any], target_size_mb: float,
                              previous_result: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Two-pass precision encoding for optimal quality/size ratio"""
        try:
            temp_output = os.path.join(self.temp_dir, "two_pass_output.mp4")
            temp_log = os.path.join(self.temp_dir, "ffmpeg2pass")
            
            # Calculate precise bitrate for target size
            target_bitrate = self._calculate_precise_bitrate(video_info, target_size_mb)
            
            # Adjust parameters based on previous attempt if available
            params = self._calculate_two_pass_params(video_info, platform_config, target_bitrate, previous_result)
            
            # Pass 1: Analysis
            ffmpeg_cmd_pass1 = self._build_two_pass_command(input_path, temp_output, params, pass_num=1, log_file=temp_log)
            self._execute_ffmpeg_with_progress(ffmpeg_cmd_pass1, video_info['duration'])
            
            # Pass 2: Encoding
            ffmpeg_cmd_pass2 = self._build_two_pass_command(input_path, temp_output, params, pass_num=2, log_file=temp_log)
            self._execute_ffmpeg_with_progress(ffmpeg_cmd_pass2, video_info['duration'])
            
            # Clean up log files
            for log_file in [f"{temp_log}-0.log", f"{temp_log}-0.log.mbtree"]:
                if os.path.exists(log_file):
                    os.remove(log_file)
            
            if os.path.exists(temp_output):
                size_mb = os.path.getsize(temp_output) / (1024 * 1024)
                quality_score = self._calculate_quality_score(params, video_info) + 1  # Bonus for two-pass
                
                return {
                    'temp_file': temp_output,
                    'size_mb': size_mb,
                    'strategy': 'two_pass',
                    'quality_score': quality_score,
                    'params': params
                }
            
        except Exception as e:
            logger.warning(f"Two-pass compression failed: {e}")
            return None
    
    def _compress_with_adaptive_resolution(self, input_path: str, video_info: Dict[str, Any], 
                                         platform_config: Dict[str, Any], target_size_mb: float) -> Optional[Dict[str, Any]]:
        """Adaptive resolution scaling based on content and size constraints"""
        try:
            temp_output = os.path.join(self.temp_dir, "adaptive_resolution_output.mp4")
            
            # Calculate optimal resolution for target size
            optimal_resolution = self._calculate_optimal_resolution(video_info, target_size_mb, platform_config)
            
            params = self._calculate_adaptive_params(video_info, platform_config, target_size_mb, optimal_resolution)
            
            ffmpeg_cmd = self._build_adaptive_ffmpeg_command(input_path, temp_output, params)
            self._execute_ffmpeg_with_progress(ffmpeg_cmd, video_info['duration'])
            
            if os.path.exists(temp_output):
                size_mb = os.path.getsize(temp_output) / (1024 * 1024)
                quality_score = self._calculate_quality_score(params, video_info)
                
                return {
                    'temp_file': temp_output,
                    'size_mb': size_mb,
                    'strategy': 'adaptive_resolution',
                    'quality_score': quality_score,
                    'params': params
                }
            
        except Exception as e:
            logger.warning(f"Adaptive resolution compression failed: {e}")
            return None
    
    def _compress_with_segmentation(self, input_path: str, output_path: str, target_size_mb: float,
                                  platform_config: Dict[str, Any], video_info: Dict[str, Any], 
                                  platform: str = None) -> Dict[str, Any]:
        """Compress video using segmentation approach"""
        try:
            logger.info("Starting video segmentation compression")
            
            # Use video segmenter to handle the segmentation
            result = self.video_segmenter.segment_video(
                input_video=input_path,
                output_base_path=output_path,
                platform=platform,
                max_size_mb=target_size_mb
            )
            
            if result.get('success', False):
                # If segmentation was successful, return the results
                if 'segments' in result:
                    # Multiple segments were created
                    total_size = sum(segment.get('size_mb', 0) for segment in result['segments'])
                    return {
                        'success': True,
                        'input_file': input_path,
                        'output_file': output_path,
                        'method': 'segmentation',
                        'original_size_mb': os.path.getsize(input_path) / (1024 * 1024),
                        'compressed_size_mb': total_size,
                        'size_mb': total_size,
                        'compression_ratio': ((os.path.getsize(input_path) - (total_size * 1024 * 1024)) / os.path.getsize(input_path)) * 100,
                        'space_saved_mb': (os.path.getsize(input_path) - (total_size * 1024 * 1024)) / (1024 * 1024),
                        'video_info': video_info,
                        'optimization_strategy': 'segmentation',
                        'quality_score': 8.0,  # High quality for segments
                        'attempts_made': 1,
                        'encoder_used': 'segmentation',
                        'segments': result['segments'],
                        'num_segments': result['num_segments'],
                        'output_folder': result.get('output_folder', ''),
                        'segment_duration': result.get('segment_duration', 0)
                    }
                else:
                    # Single file was processed
                    return result
            else:
                # Segmentation failed, fall back to standard compression
                logger.warning("Video segmentation failed, falling back to standard compression")
                return self._compress_with_standard_optimization(
                    input_path, output_path, target_size_mb, platform_config, video_info
                )
                
        except Exception as e:
            logger.error(f"Error in video segmentation compression: {e}")
            # Fall back to standard compression
            return self._compress_with_standard_optimization(
                input_path, output_path, target_size_mb, platform_config, video_info
            )
    
    def _compress_with_aggressive_optimization(self, input_path: str, video_info: Dict[str, Any], 
                                             platform_config: Dict[str, Any], target_size_mb: float) -> Optional[Dict[str, Any]]:
        """Aggressive optimization as last resort"""
        try:
            temp_output = os.path.join(self.temp_dir, "aggressive_output.mp4")
            
            # Very aggressive parameters to ensure size compliance
            params = self._calculate_aggressive_params(video_info, platform_config, target_size_mb)
            
            ffmpeg_cmd = self._build_aggressive_ffmpeg_command(input_path, temp_output, params)
            self._execute_ffmpeg_with_progress(ffmpeg_cmd, video_info['duration'])
            
            if os.path.exists(temp_output):
                size_mb = os.path.getsize(temp_output) / (1024 * 1024)
                quality_score = self._calculate_quality_score(params, video_info) - 1  # Penalty for aggressive
                
                return {
                    'temp_file': temp_output,
                    'size_mb': size_mb,
                    'strategy': 'aggressive',
                    'quality_score': quality_score,
                    'params': params
                }
            
        except Exception as e:
            logger.warning(f"Aggressive compression failed: {e}")
            return None
    
    def _calculate_intelligent_params(self, video_info: Dict[str, Any], 
                                    platform_config: Dict[str, Any], target_size_mb: float) -> Dict[str, Any]:
        """Calculate intelligent compression parameters based on content analysis"""
        
        # Get best encoder
        encoder, accel_type = self.hardware.get_best_encoder("h264")
        
        # Base parameters
        params = {
            'encoder': encoder,
            'acceleration_type': accel_type,
            'width': video_info['width'],
            'height': video_info['height'],
            'fps': min(video_info['fps'], 30),
        }
        
        # Content-aware quality adjustment
        complexity = video_info.get('complexity_score', 5.0)
        motion_level = video_info.get('motion_level', 'medium')
        
        # Adaptive CRF based on content complexity
        if accel_type == 'software':
            base_crf = 23  # Higher quality starting point
            if complexity > 7:
                params['crf'] = base_crf + 2  # Higher CRF for complex content
            elif complexity < 3:
                params['crf'] = base_crf - 2  # Lower CRF for simple content
            else:
                params['crf'] = base_crf
        
        # Motion-aware preset selection
        if motion_level == 'high':
            params['preset'] = 'faster'  # Faster preset for high motion
        elif motion_level == 'low':
            params['preset'] = 'slower'  # Slower preset for low motion
        else:
            params['preset'] = 'medium'
        
        # Intelligent bitrate calculation
        params['bitrate'] = self._calculate_content_aware_bitrate(video_info, target_size_mb)
        
        # Platform-specific adjustments
        if platform_config:
            params.update(self._apply_platform_constraints(params, platform_config))
        
        return params
    
    def _calculate_content_aware_bitrate(self, video_info: Dict[str, Any], target_size_mb: float) -> int:
        """Calculate bitrate based on content complexity and target size"""
        
        # Base calculation accounting for audio overhead
        duration = video_info['duration']
        target_bits = target_size_mb * 8 * 1024 * 1024 * 0.85  # 85% for video, 15% for audio
        base_bitrate = int(target_bits / duration / 1000)  # Convert to kbps
        
        # Adjust based on content complexity
        complexity = video_info.get('complexity_score', 5.0)
        motion_level = video_info.get('motion_level', 'medium')
        
        # Complexity adjustment factor
        if complexity > 7:
            bitrate_multiplier = 1.2  # Need more bitrate for complex content
        elif complexity < 3:
            bitrate_multiplier = 0.8  # Can use less bitrate for simple content
        else:
            bitrate_multiplier = 1.0
        
        # Motion adjustment
        motion_multipliers = {'low': 0.9, 'medium': 1.0, 'high': 1.1}
        bitrate_multiplier *= motion_multipliers.get(motion_level, 1.0)
        
        # Resolution efficiency factor
        pixel_count = video_info['width'] * video_info['height']
        if pixel_count > 1920 * 1080:  # 4K+ content
            bitrate_multiplier *= 1.3
        elif pixel_count < 1280 * 720:  # Lower resolution
            bitrate_multiplier *= 0.8
        
        final_bitrate = int(base_bitrate * bitrate_multiplier)
        
        # Ensure minimum viable bitrate
        min_bitrate = 200
        return max(final_bitrate, min_bitrate)
    
    def _calculate_precise_bitrate(self, video_info: Dict[str, Any], target_size_mb: float) -> int:
        """Calculate precise bitrate for two-pass encoding"""
        duration = video_info['duration']
        # More conservative calculation for two-pass
        target_bits = target_size_mb * 8 * 1024 * 1024 * 0.90  # 90% target utilization
        return max(int(target_bits / duration / 1000), 150)
    
    def _calculate_optimal_resolution(self, video_info: Dict[str, Any], target_size_mb: float, 
                                    platform_config: Dict[str, Any]) -> Tuple[int, int]:
        """Calculate optimal resolution for target file size"""
        
        original_width, original_height = video_info['width'], video_info['height']
        original_pixels = original_width * original_height
        
        logger.info(f"Calculating optimal resolution: original {original_width}x{original_height} "
                   f"({original_pixels:,} pixels), target size {target_size_mb}MB")
        
        # Safety check: if the target size is much larger than what we need, 
        # don't aggressively downscale. This prevents the 1.19MB issue.
        original_size_mb = video_info.get('size_bytes', 0) / (1024 * 1024)
        if original_size_mb > 0 and target_size_mb > original_size_mb * 2:
            logger.info(f"Target size {target_size_mb}MB is much larger than original {original_size_mb:.1f}MB, "
                       f"keeping original resolution to maintain quality")
            return original_width, original_height
        
        # For high-resolution videos, be much more conservative about downscaling
        # The goal is to maintain quality while meeting size constraints
        if original_pixels > 1000000:  # Over 1M pixels (like your 1080x1440)
            logger.info(f"High-resolution video detected ({original_pixels:,} pixels), using conservative scaling")
            
            # Start with a much more conservative approach
            # Instead of aggressive downscaling, try to maintain resolution and adjust other parameters
            if original_pixels <= 2000000:  # 1M-2M pixels (like 1080p, 1440p)
                # For videos in this range, try to keep at least 80% of original resolution
                min_scale_factor = 0.8
            else:  # Over 2M pixels (4K+)
                # For very high resolution, be more aggressive but still reasonable
                min_scale_factor = 0.6
            
            # Calculate what we can afford based on target size
            duration = video_info['duration']
            complexity = video_info.get('complexity_score', 5.0)
            
            # Much more conservative bitrate calculation
            target_bits = target_size_mb * 8 * 1024 * 1024 * 0.85
            bits_per_second = target_bits / duration
            
            # For high-resolution videos, use a much higher efficiency factor
            # This prevents the extreme downscaling that was happening
            base_efficiency = 0.6  # Much higher than the previous 0.25
            complexity_penalty = min(complexity * 0.002, 0.05)  # Much smaller penalty
            efficiency_factor = base_efficiency - complexity_penalty
            
            affordable_pixels = int((bits_per_second * efficiency_factor) / 24)
            
            logger.info(f"High-res calculation: duration={duration:.1f}s, complexity={complexity:.1f}, "
                       f"efficiency_factor={efficiency_factor:.3f}, affordable_pixels={affordable_pixels:,}")
            
            if affordable_pixels >= original_pixels:
                # Can keep original resolution
                optimal_width, optimal_height = original_width, original_height
                logger.info(f"Keeping original resolution: {optimal_width}x{optimal_height}")
            else:
                # Need to scale down, but be conservative
                scale_factor = math.sqrt(affordable_pixels / original_pixels)
                
                # Apply minimum scale factor to prevent extreme downscaling
                scale_factor = max(scale_factor, min_scale_factor)
                
                optimal_width = int(original_width * scale_factor)
                optimal_height = int(original_height * scale_factor)
                
                logger.info(f"Conservative scaling: factor={scale_factor:.3f}, new size={optimal_width}x{optimal_height}")
        else:
            # For lower resolution videos, use the existing logic but with improvements
            duration = video_info['duration']
            complexity = video_info.get('complexity_score', 5.0)
            
            # Improved calculation for lower resolution videos
            target_bits = target_size_mb * 8 * 1024 * 1024 * 0.85
            bits_per_second = target_bits / duration
            
            # Better efficiency factors for lower resolution
            base_efficiency = 0.35  # Increased from 0.25
            complexity_penalty = min(complexity * 0.003, 0.08)  # Reduced penalty
            efficiency_factor = base_efficiency - complexity_penalty
            
            affordable_pixels = int((bits_per_second * efficiency_factor) / 24)
            
            logger.info(f"Standard calculation: duration={duration:.1f}s, complexity={complexity:.1f}, "
                       f"efficiency_factor={efficiency_factor:.3f}, affordable_pixels={affordable_pixels:,}")
            
            if affordable_pixels >= original_pixels:
                optimal_width, optimal_height = original_width, original_height
                logger.info(f"Keeping original resolution: {optimal_width}x{optimal_height}")
            else:
                scale_factor = math.sqrt(affordable_pixels / original_pixels)
                
                # Apply minimum scale factor
                min_scale_factor = 0.6  # Never go below 60% of original
                scale_factor = max(scale_factor, min_scale_factor)
                
                optimal_width = int(original_width * scale_factor)
                optimal_height = int(original_height * scale_factor)
                
                logger.info(f"Standard scaling: factor={scale_factor:.3f}, new size={optimal_width}x{optimal_height}")
        
        # Apply platform constraints if available
        if platform_config:
            max_width = platform_config.get('max_width', optimal_width)
            max_height = platform_config.get('max_height', optimal_height)
            
            # Calculate how much we need to scale to fit within platform constraints
            # while preserving aspect ratio
            width_scale = max_width / optimal_width if optimal_width > max_width else 1.0
            height_scale = max_height / optimal_height if optimal_height > max_height else 1.0
            
            # Use the more restrictive scale factor to ensure we fit within both constraints
            scale_factor = min(width_scale, height_scale)
            
            # Apply the scale factor to maintain aspect ratio
            optimal_width = int(optimal_width * scale_factor)
            optimal_height = int(optimal_height * scale_factor)
            
            logger.info(f"Applied platform constraints: max {max_width}x{max_height}, "
                       f"scale factor: {scale_factor:.3f}, final size: {optimal_width}x{optimal_height}")
        else:
            # When no platform constraints, apply intelligent defaults based on video characteristics
            if original_height > original_width:  # Vertical video
                # For vertical videos, maintain reasonable minimums
                min_width = max(480, int(original_width * 0.7))   # At least 70% of original width
                min_height = max(640, int(original_height * 0.7)) # At least 70% of original height
            else:  # Horizontal video
                min_width = max(640, int(original_width * 0.7))   # At least 70% of original width
                min_height = max(480, int(original_height * 0.7)) # At least 70% of original height
            
            optimal_width = max(optimal_width, min_width)
            optimal_height = max(optimal_height, min_height)
            
            logger.info(f"No platform constraints, applied intelligent defaults: min {min_width}x{min_height}, "
                       f"adjusted size={optimal_width}x{optimal_height}")
        
        # Ensure even dimensions for H.264 compatibility
        optimal_width = optimal_width if optimal_width % 2 == 0 else optimal_width - 1
        optimal_height = optimal_height if optimal_height % 2 == 0 else optimal_height - 1
        
        # Final safety check - ensure reasonable minimum resolution
        # These are much higher than the previous 128x96 to prevent extreme downscaling
        if original_pixels > 1000000:  # High resolution videos
            final_min_width = 720   # Much higher minimum for high-res videos
            final_min_height = 540  # Much higher minimum for high-res videos
        else:  # Lower resolution videos
            final_min_width = 480   # Reasonable minimum for standard videos
            final_min_height = 360  # Reasonable minimum for standard videos
        
        final_width = max(optimal_width, final_min_width)
        final_height = max(optimal_height, final_min_height)

        # Never upscale beyond original resolution
        try:
            if final_width > original_width:
                final_width = original_width if original_width % 2 == 0 else original_width - 1
            if final_height > original_height:
                final_height = original_height if original_height % 2 == 0 else original_height - 1
        except Exception:
            pass
        
        logger.info(f"Final resolution: {final_width}x{final_height} "
                   f"(min allowed: {final_min_width}x{final_min_height})")
        
        return final_width, final_height
    
    def _calculate_quality_score(self, params: Dict[str, Any], video_info: Dict[str, Any]) -> float:
        """Calculate estimated quality score for comparison"""
        score = 10.0  # Start with perfect score
        
        # Resolution penalty
        original_pixels = video_info['width'] * video_info['height']
        current_pixels = params['width'] * params['height']
        resolution_factor = current_pixels / original_pixels
        score *= resolution_factor
        
        # CRF penalty (if using software encoding)
        if params.get('crf'):
            crf = params['crf']
            # CRF 18 = excellent, 23 = good, 28 = acceptable, 35+ = poor
            crf_score = max(0, (40 - crf) / 22)  # Normalize to 0-1
            score *= crf_score
        
        # Bitrate consideration
        if params.get('bitrate'):
            # Higher bitrate generally means better quality
            bitrate_bonus = min(params['bitrate'] / 2000, 1.2)  # Cap bonus at 1.2x
            score *= bitrate_bonus
        
        return max(0, min(10, score))
    
    # Include all the helper methods from the original implementation
    def _get_basic_video_info(self, video_path: str) -> Dict[str, Any]:
        """Fallback method for basic video info"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams',
                video_path
            ]
            
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=30
            )
            
            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, cmd, result.stderr)
            
            stdout_text = result.stdout or ""
            probe_data = json.loads(stdout_text) if stdout_text.strip() else {}
            
            # Find video stream
            video_stream = next(
                (stream for stream in probe_data['streams'] if stream['codec_type'] == 'video'),
                None
            )
            
            if not video_stream:
                raise ValueError("No video stream found in file")
            
            width = int(video_stream.get('width', 0))
            height = int(video_stream.get('height', 0))
            duration = float(probe_data['format'].get('duration', 0))
            
            return {
                'width': width,
                'height': height,
                'duration': duration,
                'bitrate': int(probe_data['format'].get('bit_rate', 0)),
                'fps': FFmpegUtils.parse_fps(video_stream.get('r_frame_rate', '30/1')),
                'codec': video_stream.get('codec_name', 'unknown'),
                'size_bytes': int(probe_data['format'].get('size', 0)),
                'complexity_score': 5.0,  # Default medium complexity
                'motion_level': 'medium',
                'scene_changes': max(1, int(duration / 4)),
                'aspect_ratio': width / height if height > 0 else 1.0,
                'pixel_count': width * height,
                'bitrate_per_pixel': 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get basic video info: {e}")
            raise

    def _apply_platform_constraints(self, params: Dict[str, Any], platform_config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply platform-specific constraints to parameters"""
        constraints = {}
        
        # Resolution constraints
        if 'max_width' in platform_config and 'max_height' in platform_config:
            max_width = platform_config['max_width']
            max_height = platform_config['max_height']
            
            scale_factor = min(max_width / params['width'], max_height / params['height'], 1.0)
            constraints['width'] = int(params['width'] * scale_factor)
            constraints['height'] = int(params['height'] * scale_factor)
            
            # Ensure even dimensions
            constraints['width'] = constraints['width'] if constraints['width'] % 2 == 0 else constraints['width'] - 1
            constraints['height'] = constraints['height'] if constraints['height'] % 2 == 0 else constraints['height'] - 1
        
        # FPS constraints
        if 'fps' in platform_config:
            constraints['fps'] = min(platform_config['fps'], params['fps'])
        
        return constraints
    
    def _calculate_two_pass_params(self, video_info: Dict[str, Any], platform_config: Dict[str, Any], 
                                 target_bitrate: int, previous_result: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate parameters for two-pass encoding"""
        # Force software encoding for two-pass; hardware encoders generally don't support it reliably
        encoder, accel_type = self.hardware.get_best_encoder("h264")
        if accel_type != 'software':
            encoder = 'libx264'
            accel_type = 'software'
        
        params = {
            'encoder': encoder,
            'acceleration_type': accel_type,
            'width': video_info['width'],
            'height': video_info['height'],
            'fps': min(video_info['fps'], 30),
            'bitrate': target_bitrate,
            'preset': 'slow',  # Use slower preset for two-pass
        }
        
        # Adjust based on previous attempt
        if previous_result and previous_result.get('size_mb', 0) > 0:
            previous_params = previous_result.get('params', {})
            # Fine-tune bitrate based on previous result
            if previous_result['size_mb'] > target_bitrate * video_info['duration'] / (8 * 1024):
                params['bitrate'] = int(target_bitrate * 0.9)  # Reduce bitrate
        
        # Apply platform constraints
        if platform_config:
            params.update(self._apply_platform_constraints(params, platform_config))
        
        return params
    
    def _calculate_adaptive_params(self, video_info: Dict[str, Any], platform_config: Dict[str, Any], 
                                 target_size_mb: float, optimal_resolution: Tuple[int, int]) -> Dict[str, Any]:
        """Calculate parameters for adaptive resolution encoding"""
        
        encoder, accel_type = self.hardware.get_best_encoder("h264")
        
        params = {
            'encoder': encoder,
            'acceleration_type': accel_type,
            'width': optimal_resolution[0],
            'height': optimal_resolution[1],
            'fps': min(video_info['fps'], 30),
            'preset': 'medium',
        }
        
        # Calculate bitrate for new resolution
        pixel_ratio = (optimal_resolution[0] * optimal_resolution[1]) / (video_info['width'] * video_info['height'])
        base_bitrate = self._calculate_content_aware_bitrate(video_info, target_size_mb)
        params['bitrate'] = int(base_bitrate * pixel_ratio * 1.1)  # Slight bonus for resolution change
        
        # CRF for software encoding
        if accel_type == 'software':
            params['crf'] = 25  # Balanced quality for adaptive resolution
        
        return params
    
    def _calculate_aggressive_params(self, video_info: Dict[str, Any], platform_config: Dict[str, Any], 
                                   target_size_mb: float) -> Dict[str, Any]:
        """Calculate aggressive compression parameters as last resort"""
        
        encoder, accel_type = self.hardware.get_best_encoder("h264")
        
        original_pixels = video_info['width'] * video_info['height']
        logger.info(f"Aggressive compression: original {video_info['width']}x{video_info['height']} "
                   f"({original_pixels:,} pixels), target size {target_size_mb}MB")
        
        # Much less aggressive resolution reduction for high-resolution videos
        if original_pixels > 1000000:  # High resolution (like your 1080x1440)
            # For high-res videos, be very conservative about downscaling
            scale_factor = 0.9  # Only reduce to 90% of original (was 0.8)
            logger.info(f"High-resolution video detected, using conservative scale factor: {scale_factor}")
        else:
            # For lower resolution videos, use standard aggressive scaling
            scale_factor = 0.8  # Standard aggressive scaling
            logger.info(f"Standard resolution video, using aggressive scale factor: {scale_factor}")
        
        aggressive_width = int(video_info['width'] * scale_factor)
        aggressive_height = int(video_info['height'] * scale_factor)
        
        logger.info(f"Initial aggressive scaling: factor={scale_factor}, size={aggressive_width}x{aggressive_height}")
        
        # Apply much better minimum resolution constraints to prevent extreme downscaling
        if video_info['height'] > video_info['width']:  # Vertical video
            if original_pixels > 1000000:  # High resolution
                min_width = max(720, int(video_info['width'] * 0.8))   # At least 720px wide or 80% of original
                min_height = max(960, int(video_info['height'] * 0.8)) # At least 960px tall or 80% of original
            else:  # Standard resolution
                min_width = max(640, int(video_info['width'] * 0.7))   # At least 640px wide or 70% of original
                min_height = max(480, int(video_info['height'] * 0.7)) # At least 480px tall or 70% of original
        else:  # Horizontal video
            if original_pixels > 1000000:  # High resolution
                min_width = max(960, int(video_info['width'] * 0.8))   # At least 960px wide or 80% of original
                min_height = max(720, int(video_info['height'] * 0.8)) # At least 720px tall or 80% of original
            else:  # Standard resolution
                min_width = max(640, int(video_info['width'] * 0.7))   # At least 640px wide or 70% of original
                min_height = max(480, int(video_info['height'] * 0.7)) # At least 480px tall or 70% of original
        
        aggressive_width = max(aggressive_width, min_width)
        aggressive_height = max(aggressive_height, min_height)
        
        logger.info(f"Applied minimum constraints: min {min_width}x{min_height}, "
                   f"adjusted size={aggressive_width}x{aggressive_height}")
        
        # Ensure even dimensions
        aggressive_width = aggressive_width if aggressive_width % 2 == 0 else aggressive_width - 1
        aggressive_height = aggressive_height if aggressive_height % 2 == 0 else aggressive_height - 1
        
        params = {
            'encoder': encoder,
            'acceleration_type': accel_type,
            'width': aggressive_width,
            'height': aggressive_height,
            'fps': min(video_info['fps'], 24),  # Reduce FPS
            'preset': 'veryfast',  # Fast preset for aggressive compression
        }
        
        # Very conservative bitrate
        duration = video_info['duration']
        target_bits = target_size_mb * 8 * 1024 * 1024 * 0.75  # Use only 75% of target
        params['bitrate'] = max(int(target_bits / duration / 1000), 100)
        
        # High CRF for software encoding
        if accel_type == 'software':
            params['crf'] = 35  # Very high CRF for maximum compression
        
        logger.info(f"Final aggressive params: {aggressive_width}x{aggressive_height}, "
                   f"bitrate={params['bitrate']}k, crf={params.get('crf', 'N/A')}")
        
        return params
    
    def _build_intelligent_ffmpeg_command(self, input_path: str, output_path: str, 
                                        params: Dict[str, Any]) -> List[str]:
        """Build FFmpeg command with intelligent parameters"""
        params['maxrate_multiplier'] = 1.2  # Set specific multiplier for intelligent command
        return FFmpegUtils.build_standard_ffmpeg_command(input_path, output_path, params)
    
    def _build_two_pass_command(self, input_path: str, output_path: str, params: Dict[str, Any], 
                              pass_num: int, log_file: str) -> List[str]:
        """Build two-pass FFmpeg command"""
        params['maxrate_multiplier'] = 1.1  # Set specific multiplier for two-pass
        return FFmpegUtils.build_two_pass_command(input_path, output_path, params, pass_num, log_file)
    
    def _build_adaptive_ffmpeg_command(self, input_path: str, output_path: str, 
                                     params: Dict[str, Any]) -> List[str]:
        """Build adaptive FFmpeg command with smart filtering"""
        
        # Use shared utilities for base command
        params['maxrate_multiplier'] = 1.15
        cmd = FFmpegUtils.build_base_ffmpeg_command(input_path, output_path, params)
        
        # Smart scaling with high-quality filter and normalized SAR
        scale_filter = f"scale={params['width']}:{params['height']}:flags=lanczos,setsar=1"
        cmd.extend(['-vf', scale_filter])
        
        # Add frame rate
        if 'fps' in params:
            cmd.extend(['-r', str(params['fps'])])
        
        # Quality settings for software encoding
        if params.get('acceleration_type') == 'software':
            if 'crf' in params:
                cmd.extend(['-crf', str(params['crf'])])
            cmd.extend(['-preset', params.get('preset', 'medium')])
        
        # Use shared utilities for remaining settings
        cmd = FFmpegUtils.add_bitrate_control(cmd, params, buffer_multiplier=1.5)
        cmd = FFmpegUtils.add_audio_settings(cmd, params)
        cmd = FFmpegUtils.add_output_optimizations(cmd, output_path)
        
        logger.debug(f"Adaptive FFmpeg command: {' '.join(cmd)}")
        return cmd
    
    def _build_aggressive_ffmpeg_command(self, input_path: str, output_path: str, 
                                       params: Dict[str, Any]) -> List[str]:
        """Build aggressive compression FFmpeg command"""
        
        # Set aggressive parameters
        params['maxrate_multiplier'] = 1.0  # No tolerance
        params['audio_bitrate'] = 64  # Lower audio quality
        params['audio_channels'] = 1  # Mono audio
        
        # Use shared utilities for base command
        cmd = FFmpegUtils.build_base_ffmpeg_command(input_path, output_path, params)
        cmd = FFmpegUtils.add_video_settings(cmd, params)
        
        # Aggressive quality settings
        if params.get('acceleration_type') == 'software':
            cmd.extend(['-crf', str(params.get('crf', 35))])
            cmd.extend(['-preset', params.get('preset', 'veryfast')])
        
        # Strict bitrate control with small buffer
        cmd = FFmpegUtils.add_bitrate_control(cmd, params, buffer_multiplier=0.5)
        cmd = FFmpegUtils.add_audio_settings(cmd, params)
        cmd = FFmpegUtils.add_output_optimizations(cmd, output_path)
        
        logger.debug(f"Aggressive FFmpeg command: {' '.join(cmd)}")
        return cmd
    
    def _execute_ffmpeg_with_progress(self, cmd: List[str], duration: float):
        """Execute FFmpeg command with progress bar and hardware fallback"""
        
        logger.debug("Starting FFmpeg compression...")
        logger.debug(f"FFmpeg command: {' '.join(cmd)}")
        
        # Try original command first
        try:
            self._execute_ffmpeg_command(cmd, duration)
            logger.info("FFmpeg compression completed")
        except subprocess.CalledProcessError as e:
            # Check if it's a hardware acceleration error
            error_output = str(e.stderr) if e.stderr else str(e)
            logger.error(f"FFmpeg command failed with error: {error_output[:500]}...")  # Limit error output length
            
            # Enhanced hardware error detection patterns
            hardware_error_patterns = [
                # AMD AMF specific errors
                'amf', 'h264_amf', 'hevc_amf', 'av1_amf',
                'failed to initialize amf', 'amf encoder init failed',
                'cannot load amfrt64.dll', 'cannot load amfrt32.dll',
                'no amf device found', 'amf session init failed',
                
                # NVIDIA NVENC specific errors
                'nvenc', 'h264_nvenc', 'hevc_nvenc', 'av1_nvenc',
                'cannot load nvcuda.dll', 'cuda driver not found',
                'nvenc init failed', 'no nvidia device found',
                
                # Intel QuickSync specific errors
                'qsv', 'h264_qsv', 'hevc_qsv', 'mfx session',
                'qsv init failed', 'no qsv device found',
                
                # General hardware acceleration errors
                'hardware', 'hwaccel', 'gpu', 'device not found',
                'encoder not found', 'codec not supported'
            ]
            
            is_hardware_error = any(pattern in error_output.lower() for pattern in hardware_error_patterns)
            
            # Additional check for specific error codes that indicate hardware issues
            hardware_error_codes = [4294967274, -22, -12, -2]  # Common hardware failure codes
            is_hardware_error = is_hardware_error or (hasattr(e, 'returncode') and e.returncode in hardware_error_codes)
            
            if is_hardware_error:
                # Determine the type of hardware encoder that failed
                encoder_type = "Unknown"
                if any(amd in error_output.lower() for amd in ['amf', 'h264_amf', 'hevc_amf']):
                    encoder_type = "AMD AMF"
                elif any(nvidia in error_output.lower() for nvidia in ['nvenc', 'h264_nvenc', 'hevc_nvenc']):
                    encoder_type = "NVIDIA NVENC"
                elif any(intel in error_output.lower() for intel in ['qsv', 'h264_qsv', 'hevc_qsv']):
                    encoder_type = "Intel QuickSync"
                
                logger.warning(f"{encoder_type} hardware acceleration failed, trying software fallback...")
                
                # Replace hardware encoder with software encoder
                fallback_cmd = self._create_software_fallback_command(cmd)
                if fallback_cmd:
                    logger.debug(f"Fallback command: {' '.join(fallback_cmd)}")
                    try:
                        self._execute_ffmpeg_command(fallback_cmd, duration)
                        logger.info("FFmpeg compression completed with software fallback")
                        return
                    except subprocess.CalledProcessError as fallback_error:
                        logger.error(f"Software fallback also failed: {str(fallback_error)[:200]}...")
                        pass  # Fall through to original error
                else:
                    logger.error("Failed to create software fallback command")
            
            # Re-raise original error if fallback didn't work or wasn't attempted
            raise e
    
    def _execute_ffmpeg_command(self, cmd: List[str], duration: float):
        """Execute FFmpeg command with progress bar (internal method)"""
        # Check for shutdown before starting
        if self.shutdown_requested:
            raise subprocess.CalledProcessError(1, cmd, "Shutdown requested before FFmpeg execution")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1,
            encoding='utf-8',
            errors='replace'
        )
        
        # Store reference to current process for shutdown handling
        self.current_ffmpeg_process = process
        
        # Capture stderr output for error analysis
        stderr_output = []
        
        try:
            # Create progress bar
            with tqdm(total=100, desc="Compressing", unit="%", bar_format="{l_bar}{bar}| {n:.1f}%") as pbar:
                
                while True:
                    # Check for shutdown request
                    if self.shutdown_requested:
                        logger.info("Shutdown requested during FFmpeg execution, terminating process...")
                        self._terminate_ffmpeg_process()
                        raise subprocess.CalledProcessError(1, cmd, "Shutdown requested during execution")
                    
                    # Check if process has finished
                    if process.poll() is not None:
                        break
                    
                    # Read stderr output with timeout to allow shutdown checking
                    try:
                        output = process.stderr.readline()
                        if output == '':
                            # No more output, check if process is done
                            if process.poll() is not None:
                                break
                            continue
                        
                        if output:
                            # Store stderr output for error analysis
                            stderr_output.append(output)
                            
                            # Parse FFmpeg progress output
                            if 'time=' in output:
                                try:
                                    time_str = output.split('time=')[1].split()[0]
                                    current_seconds = self._parse_time_to_seconds(time_str)
                                    progress = min((current_seconds / duration) * 100, 100)
                                    pbar.n = progress
                                    pbar.refresh()
                                except:
                                    pass  # Ignore parsing errors
                    except Exception as e:
                        logger.debug(f"Error reading FFmpeg output: {e}")
                        break
            
            # Wait for process to complete (with timeout for shutdown checking)
            return_code = process.wait()
            
        except Exception as e:
            # Ensure process is cleaned up
            if process.poll() is None:
                self._terminate_ffmpeg_process()
            raise e
        finally:
            # Clear current process reference
            self.current_ffmpeg_process = None
        
        if return_code != 0:
            # Join all stderr output for error analysis
            full_stderr_output = ''.join(stderr_output)
            
            # Check if this is an AMD AMF encoder error
            if any(encoder in ' '.join(cmd) for encoder in ['h264_amf', 'hevc_amf', 'av1_amf']):
                # Check for specific AMD AMF error patterns
                amd_error_patterns = [
                    'Invalid argument',
                    'Failed to initialize AMF',
                    'AMF encoder init failed',
                    'No AMF device found',
                    'AMF session init failed',
                    'Cannot load amfrt64.dll',
                    'Cannot load amfrt32.dll'
                ]
                
                # Convert unsigned error code to signed for comparison
                signed_return_code = return_code if return_code < 2147483648 else return_code - 4294967296
                
                is_amd_error = (
                    str(return_code) == '4294967274' or  # Unsigned version of -22
                    signed_return_code == -22 or          # Signed version (Invalid argument)
                    any(pattern in full_stderr_output for pattern in amd_error_patterns)
                )
                
                if is_amd_error:
                    logger.warning(f"AMD AMF encoder failed with error code {return_code} (signed: {signed_return_code}), attempting software fallback...")
                    logger.debug(f"AMD AMF error details: {full_stderr_output[-500:]}")  # Log last 500 chars of stderr
                    
                    # Create software fallback command
                    fallback_cmd = self._create_software_fallback_command(cmd)
                    if fallback_cmd:
                        logger.info("Replaced h264_amf with libx264 for software fallback")
                        logger.info("Attempting software fallback...")
                        # Try the fallback command
                        try:
                            return self._execute_ffmpeg_command(fallback_cmd, duration)
                        except subprocess.CalledProcessError as fallback_error:
                            logger.error(f"Software fallback also failed: {fallback_error}")
                            raise fallback_error
                    else:
                        logger.error("Failed to create software fallback command")
            
            raise subprocess.CalledProcessError(return_code, cmd, full_stderr_output)
    
    def _create_software_fallback_command(self, cmd: List[str]) -> Optional[List[str]]:
        """Create a software fallback version of an FFmpeg command"""
        try:
            fallback_cmd = cmd.copy()
            
            # Replace hardware encoders with software equivalents
            encoder_replacements = {
                'h264_qsv': 'libx264',
                'h264_nvenc': 'libx264', 
                'h264_amf': 'libx264',
                'hevc_qsv': 'libx265',
                'hevc_nvenc': 'libx265',
                'hevc_amf': 'libx265',
                'av1_amf': 'libsvtav1'  # AV1 software encoder
            }
            
            encoder_replaced = False
            for i, arg in enumerate(fallback_cmd):
                if arg in encoder_replacements:
                    old_encoder = arg
                    new_encoder = encoder_replacements[arg]
                    fallback_cmd[i] = new_encoder
                    encoder_replaced = True
                    logger.info(f"Replaced {old_encoder} with {new_encoder} for software fallback")
            
            if not encoder_replaced:
                logger.warning("No hardware encoder found to replace in fallback command")
            
            # Remove hardware-specific options that don't work with software encoders
            hardware_options_to_remove = [
                '-hwaccel', 'cuda', '-hwaccel', 'auto', '-hwaccel', 'qsv', '-hwaccel', 'dxva2',
                # AMD AMF specific options
                '-usage', 'transcoding', '-usage', 'lowlatency', '-usage', 'ultralowlatency',
                '-quality', 'speed', '-quality', 'balanced', '-quality', 'quality',
                '-rc', 'cbr', '-rc', 'vbr', '-rc', 'cqp',
                '-enforce_hrd', '-filler_data', '-frame_skipping', '-vbaq', '-preanalysis',
                # NVIDIA NVENC specific options
                '-preset', 'p1', '-preset', 'p2', '-preset', 'p3', '-preset', 'p4', 
                '-preset', 'p5', '-preset', 'p6', '-preset', 'p7',
                '-tune', 'hq', '-tune', 'll', '-tune', 'ull',
                # Intel QSV specific options
                '-global_quality', '-look_ahead', '-look_ahead_depth'
            ]
            
            # Remove hardware options and their values
            i = 0
            while i < len(fallback_cmd):
                if fallback_cmd[i] in hardware_options_to_remove:
                    option = fallback_cmd[i]
                    fallback_cmd.pop(i)  # Remove the option
                    # Check if the next argument is a value (not starting with -)
                    if i < len(fallback_cmd) and not fallback_cmd[i].startswith('-'):
                        value = fallback_cmd[i]
                        fallback_cmd.pop(i)  # Remove the value
                        logger.debug(f"Removed hardware option: {option} {value}")
                    else:
                        logger.debug(f"Removed hardware option: {option}")
                else:
                    i += 1
            
            # Convert hardware-specific quality settings to software equivalents
            for i, arg in enumerate(fallback_cmd):
                # Convert QP (quantization parameter) to CRF for software encoders
                if arg == '-qp' and i + 1 < len(fallback_cmd):
                    fallback_cmd[i] = '-crf'
                    # QP and CRF have similar ranges, so keep the value
                    logger.debug(f"Converted -qp to -crf for software encoding")
                
                # Convert NVENC CQ to CRF
                elif arg == '-cq' and i + 1 < len(fallback_cmd):
                    fallback_cmd[i] = '-crf'
                    logger.debug(f"Converted -cq to -crf for software encoding")
            
            # Add software encoder optimizations
            if 'libx264' in fallback_cmd:
                # Add reasonable preset if not present
                if '-preset' not in fallback_cmd:
                    fallback_cmd.extend(['-preset', 'medium'])
                    logger.debug("Added -preset medium for libx264")
            
            elif 'libx265' in fallback_cmd:
                # Add reasonable preset if not present
                if '-preset' not in fallback_cmd:
                    fallback_cmd.extend(['-preset', 'medium'])
                    logger.debug("Added -preset medium for libx265")
            
            return fallback_cmd
            
        except Exception as e:
            logger.warning(f"Failed to create software fallback command: {e}")
            return None
    
    def _parse_time_to_seconds(self, time_str: str) -> float:
        """Parse FFmpeg time format (HH:MM:SS.mmm) to seconds"""
        try:
            parts = time_str.split(':')
            hours = float(parts[0])
            minutes = float(parts[1])
            seconds = float(parts[2])
            return hours * 3600 + minutes * 60 + seconds
        except:
            return 0.0
    
    def _get_compression_results(self, input_path: str, output_path: str, 
                               video_info: Dict[str, Any], method: str) -> Dict[str, Any]:
        """Generate compression results summary"""
        
        original_size = os.path.getsize(input_path)
        compressed_size = os.path.getsize(output_path)
        
        compression_ratio = ((original_size - compressed_size) / original_size) * 100
        compressed_size_mb = compressed_size / (1024 * 1024)
        
        # Log detailed file specifications
        try:
            from .ffmpeg_utils import FFmpegUtils
            specs = FFmpegUtils.get_detailed_file_specifications(output_path)
            specs_log = FFmpegUtils.format_file_specifications_for_logging(specs)
            logger.info(f"Video compression completed successfully - {specs_log}")
        except Exception as e:
            logger.warning(f"Could not log detailed video specifications: {e}")
        
        return {
            'success': True,  # Add success flag for automated workflow
            'input_file': input_path,
            'output_file': output_path,
            'method': method,
            'original_size_mb': original_size / (1024 * 1024),
            'compressed_size_mb': compressed_size_mb,
            'size_mb': compressed_size_mb,  # Add alias for automated workflow
            'compression_ratio': compression_ratio,
            'space_saved_mb': (original_size - compressed_size) / (1024 * 1024),
            'video_info': video_info,
            'encoder_used': getattr(self, '_last_encoder_used', 'unknown')
        }
    
    def _get_error_results(self, input_path: str, output_path: str, error_message: str) -> Dict[str, Any]:
        """Generate error results for failed compression"""
        return {
            'success': False,
            'input_file': input_path,
            'output_file': output_path,
            'error': error_message,
            'method': 'failed',
            'original_size_mb': os.path.getsize(input_path) / (1024 * 1024) if os.path.exists(input_path) else 0,
            'compressed_size_mb': 0,
            'size_mb': 0,
            'compression_ratio': 0,
            'space_saved_mb': 0,
            'encoder_used': 'none'
        }

    def _calculate_compression_params_with_quality(self, video_info: Dict[str, Any], 
                                                 platform_config: Dict[str, Any], 
                                                 target_size_mb: float,
                                                 quality_params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate compression parameters with specific quality level"""
        
        # Get best encoder
        encoder, accel_type = self.hardware.get_best_encoder("h264")
        
        # Base parameters
        params = {
            'encoder': encoder,
            'acceleration_type': accel_type,
            'width': video_info['width'],
            'height': video_info['height'],
            'fps': min(video_info['fps'], 30),
        }
        
        # Apply quality-specific settings
        if accel_type == 'software':
            params['crf'] = quality_params.get('crf', 23)
            params['preset'] = quality_params.get('preset', 'medium')
        
        # Calculate bitrate based on quality priority
        if quality_params.get('priority') == 'speed':
            # Faster processing, less optimal bitrate
            params['bitrate'] = int(self._calculate_content_aware_bitrate(video_info, target_size_mb) * 1.1)
        elif quality_params.get('priority') == 'quality':
            # Quality priority, more conservative bitrate
            params['bitrate'] = int(self._calculate_content_aware_bitrate(video_info, target_size_mb) * 0.9)
        else:
            # Balanced
            params['bitrate'] = self._calculate_content_aware_bitrate(video_info, target_size_mb)
        
        # Platform-specific adjustments
        if platform_config:
            params.update(self._apply_platform_constraints(params, platform_config))
        
        return params
    
    def batch_compress_videos(self, video_list: List[str], output_dir: str, 
                            platform: str = None, max_size_mb: float = None) -> Dict[str, Any]:
        """
        Batch compress multiple videos with intelligent processing
        """
        
        logger.info(f"Starting batch compression of {len(video_list)} videos")
        
        # Create processing function for batch
        def process_single_video(file_info):
            input_path = file_info['input_path']
            filename = os.path.basename(input_path)
            name, ext = os.path.splitext(filename)
            output_path = os.path.join(output_dir, f"{name}_compressed{ext}")
            
            try:
                result = self.compress_video(
                    input_path=input_path,
                    output_path=output_path,
                    platform=platform,
                    max_size_mb=max_size_mb,
                    use_advanced_optimization=True
                )
                
                return {
                    'success': True,
                    'input_path': input_path,
                    'output_path': output_path,
                    'result': result
                }
                
            except Exception as e:
                logger.error(f"Failed to compress {input_path}: {e}")
                return {
                    'success': False,
                    'input_path': input_path,
                    'error': str(e)
                }
        
        # Use intelligent batch processing
        batch_results = self.performance_enhancer.intelligent_batch_processing(
            video_list, process_single_video
        )
        
        # Compile final results
        successful = [r for r in batch_results if r.get('success', False)]
        failed = [r for r in batch_results if not r.get('success', False)]
        
        return {
            'total_processed': len(video_list),
            'successful': len(successful),
            'failed': len(failed),
            'successful_results': successful,
            'failed_results': failed,
            'performance_stats': self.performance_enhancer.get_performance_stats()
        }
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get comprehensive optimization statistics"""
        
        stats = {
            'performance_stats': self.performance_enhancer.get_performance_stats(),
            'system_optimizations': self.system_optimizations,
            'hardware_info': {
                'best_encoder': self.hardware.get_best_encoder("h264"),
                'has_hardware_acceleration': self.hardware.has_hardware_acceleration(),
                'gpu_info': [gpu for gpu in self.hardware.gpu_info if gpu],
                'system_report': self.hardware.get_system_report()
            }
        }
        
        return stats

    def request_shutdown(self):
        """Request graceful shutdown of the compressor"""
        logger.info("Shutdown requested for video compressor")
        self.shutdown_requested = True
        if self.current_ffmpeg_process:
            logger.info("Terminating current FFmpeg process...")
            self._terminate_ffmpeg_process()
    
    def _terminate_ffmpeg_process(self):
        """Terminate the current FFmpeg process gracefully"""
        if self.current_ffmpeg_process and self.current_ffmpeg_process.poll() is None:
            try:
                # Try graceful termination first
                self.current_ffmpeg_process.terminate()
                
                # Wait a bit for graceful termination
                try:
                    self.current_ffmpeg_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if graceful termination fails
                    logger.warning("FFmpeg process did not terminate gracefully, forcing kill...")
                    self.current_ffmpeg_process.kill()
                    self.current_ffmpeg_process.wait()
                
                logger.info("FFmpeg process terminated successfully")
            except Exception as e:
                logger.error(f"Error terminating FFmpeg process: {e}")
            finally:
                self.current_ffmpeg_process = None

# Keep all the existing methods from the original VideoCompressor class
# by creating an alias for backward compatibility
VideoCompressor = DynamicVideoCompressor 