"""
PDF Report Generator
Generates comprehensive PDF reports for detection results
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    Image, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np


class PDFReportGenerator:
    """Generates PDF reports for deepfake detection results"""

    def __init__(self, job_dir: Path):
        self.job_dir = Path(job_dir)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))

        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12,
            spaceBefore=12
        ))

        # Verdict style (for fake/real)
        self.styles.add(ParagraphStyle(
            name='VerdictFake',
            parent=self.styles['Normal'],
            fontSize=18,
            textColor=colors.red,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='VerdictReal',
            parent=self.styles['Normal'],
            fontSize=18,
            textColor=colors.green,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

    def _load_json(self, filename: str) -> Optional[Dict]:
        """Load JSON file from job directory"""
        filepath = self.job_dir / filename
        if not filepath.exists():
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def _create_timeline_chart(self, timeline_data: Dict) -> Optional[str]:
        """Create timeline chart from DeepfakeBench data"""
        try:
            if not timeline_data or "segments" not in timeline_data:
                return None

            segments = timeline_data["segments"]
            if not segments:
                return None

            # Create figure
            fig, ax = plt.subplots(figsize=(10, 4))

            # Plot segments
            for i, segment in enumerate(segments):
                start = segment["start_time"]
                end = segment["end_time"]
                score = segment["avg_score"]

                # Color based on score
                color = 'red' if score > 0.5 else 'yellow' if score > 0.3 else 'green'
                ax.barh(0, end - start, left=start, height=0.5, color=color, alpha=0.7)

                # Add score label
                mid = (start + end) / 2
                ax.text(mid, 0, f'{score:.2f}', ha='center', va='center', fontsize=8)

            ax.set_ylim(-0.5, 0.5)
            ax.set_xlabel('Time (seconds)')
            ax.set_title('Suspicious Segments Timeline')
            ax.set_yticks([])

            # Save to file
            chart_path = self.job_dir / "timeline_chart.png"
            plt.tight_layout()
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()

            return str(chart_path)
        except Exception as e:
            print(f"Warning: Failed to create timeline chart: {e}")
            return None

    def _create_score_distribution(self, timeline_data: Dict) -> Optional[str]:
        """Create score distribution histogram"""
        try:
            if not timeline_data or "frame_scores" not in timeline_data:
                return None

            frame_scores = timeline_data["frame_scores"]
            if not frame_scores:
                return None

            scores = [fs["score"] for fs in frame_scores]

            # Create histogram
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.hist(scores, bins=20, color='steelblue', alpha=0.7, edgecolor='black')
            ax.set_xlabel('Fake Score')
            ax.set_ylabel('Frame Count')
            ax.set_title('Score Distribution')
            ax.axvline(x=0.5, color='red', linestyle='--', label='Threshold (0.5)')
            ax.legend()

            # Save to file
            chart_path = self.job_dir / "score_distribution.png"
            plt.tight_layout()
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()

            return str(chart_path)
        except Exception as e:
            print(f"Warning: Failed to create score distribution: {e}")
            return None

    def generate_report(self, metadata: Dict) -> str:
        """
        Generate comprehensive PDF report

        Args:
            metadata: Job metadata including detection results

        Returns:
            Path to generated PDF file
        """
        output_path = self.job_dir / "report.pdf"

        # Create PDF document
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )

        # Build content
        story = []

        # Header
        story.append(Paragraph("VAJRA Trust Intelligence Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))

        # Job Information Section
        story.append(Paragraph("Job Information", self.styles['CustomSubtitle']))

        job_info_data = [
            ["Job ID:", metadata.get("job_id", "N/A")],
            ["Filename:", metadata.get("filename", "N/A")],
            ["Detection Type:", metadata.get("detection_type", "N/A").upper()],
            ["Model:", metadata.get("model", "N/A")],
            ["Analyzed By:", metadata.get("username", "N/A")],
            ["Created:", metadata.get("created_at", "N/A")[:19]],
            ["Completed:", metadata.get("completed_at", "N/A")[:19] if metadata.get("completed_at") else "N/A"],
        ]

        job_table = Table(job_info_data, colWidths=[2*inch, 4.5*inch])
        job_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#333333')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        story.append(job_table)
        story.append(Spacer(1, 0.3*inch))

        # Executive Summary Section
        result = metadata.get("result", {})
        detection_type = metadata.get("detection_type", "").lower()

        story.append(Paragraph("Executive Summary", self.styles['CustomSubtitle']))

        verdict = result.get("verdict", "unknown").upper()
        score = result.get("score", 0)

        # Generate executive summary text based on verdict
        if verdict == "FAKE":
            risk_level = "HIGH" if score > 0.7 else "MODERATE"
            summary_text = (
                f"This analysis indicates a <b>{risk_level} RISK</b> of manipulation. "
                f"The content has been classified as <b>FAKE</b> with a detection score of <b>{score:.1%}</b>. "
            )
        elif verdict == "REAL":
            confidence_level = "HIGH" if score > 0.7 else "MODERATE"
            summary_text = (
                f"This analysis indicates <b>{confidence_level} CONFIDENCE</b> in authenticity. "
                f"The content has been classified as <b>REAL</b> with an authenticity score of <b>{score:.1%}</b>. "
            )
        else:
            summary_text = "Analysis completed with inconclusive results. "

        # Add detection-type-specific summary
        if detection_type == "trufor":
            summary_text += "Pixel-level forensic analysis was performed to detect image manipulation."
        elif detection_type == "deepfakebench":
            model_name = result.get("model_name", metadata.get("model", "Unknown"))
            total_frames = result.get("total_frames", 0)
            summary_text += f"Frame-level deepfake detection was performed using the <b>{model_name}</b> model on {total_frames} frames."

        story.append(Paragraph(summary_text, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))

        # Detection Results Section
        story.append(Paragraph("Detection Results", self.styles['CustomSubtitle']))

        # Verdict with color
        verdict_style = self.styles['VerdictFake'] if verdict == "FAKE" else self.styles['VerdictReal']
        story.append(Paragraph(f"<b>Verdict:</b> {verdict}", verdict_style))
        story.append(Spacer(1, 0.1*inch))

        # Score details - varies by detection type
        if detection_type == "trufor":
            # TruFor-specific scores
            integrity = result.get("integrity", 0)
            fake_prob = result.get("fake_prob", 0)
            confidence = result.get("confidence", 0)

            score_data = [
                ["<b>Authenticity Score:</b>", f"{score:.2%}"],
                ["<b>Integrity Score:</b>", f"{integrity:.2%}"],
                ["<b>Fake Probability:</b>", f"{fake_prob:.2%}"],
                ["<b>Confidence:</b>", f"{confidence:.2%}"],
            ]

            # Add image size if available
            image_size = result.get("image_size")
            if image_size:
                score_data.append(["<b>Image Size:</b>", f"{image_size[0]}×{image_size[1]} pixels"])

            score_table = Table(score_data, colWidths=[2*inch, 4.5*inch])
            score_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(score_table)

            # Portrait mode note if present
            portrait_note = result.get("portrait_note", "")
            if portrait_note:
                story.append(Spacer(1, 0.1*inch))
                note_para = Paragraph(
                    f"<i><b>Note:</b> {portrait_note}</i>",
                    self.styles['Normal']
                )
                story.append(note_para)

        elif detection_type == "deepfakebench":
            # DeepfakeBench-specific scores
            avg_score = result.get("average_score", score)
            confidence = result.get("confidence", 0)
            fps = result.get("fps", 0)
            threshold = result.get("threshold", 0.5)
            total_frames = result.get("total_frames", 0)
            suspicious_frames = result.get("suspicious_frames", 0)
            suspicious_segments = result.get("suspicious_segments", 0)

            # Calculate video duration
            video_duration = total_frames / fps if fps > 0 else 0

            score_data = [
                ["<b>Overall Score:</b>", f"{score:.2%}"],
                ["<b>Average Frame Score:</b>", f"{avg_score:.2%}"],
                ["<b>Confidence:</b>", f"{confidence:.2%}"],
                ["<b>Detection Threshold:</b>", f"{threshold:.2%}"],
                ["<b>Video Duration:</b>", f"{video_duration:.1f}s ({total_frames} frames)"],
                ["<b>Sampling Rate:</b>", f"{fps:.1f} FPS"],
                ["<b>Suspicious Frames:</b>", f"{suspicious_frames} / {total_frames} ({suspicious_frames/total_frames*100:.1f}%)" if total_frames > 0 else "N/A"],
                ["<b>Suspicious Segments:</b>", f"{suspicious_segments}"],
            ]

            score_table = Table(score_data, colWidths=[2.2*inch, 4.3*inch])
            score_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(score_table)
        else:
            # Generic score display
            score_text = f"<b>Confidence Score:</b> {score:.2%}" if score else "Score: N/A"
            story.append(Paragraph(score_text, self.styles['Normal']))

        story.append(Spacer(1, 0.3*inch))

        # Timeline Data (for DeepfakeBench)
        timeline = self._load_json("timeline.json")
        if timeline:
            story.append(Paragraph("Timeline Analysis", self.styles['CustomSubtitle']))

            # Summary statistics
            summary_data = timeline.get("summary", {})
            if summary_data:
                summary_info = [
                    ["Total Frames:", str(summary_data.get("total_frames", "N/A"))],
                    ["Suspicious Frames:", str(summary_data.get("suspicious_frames", "N/A"))],
                    ["Suspicious Segments:", str(summary_data.get("suspicious_segments", "N/A"))],
                    ["Average Score:", f"{summary_data.get('average_score', 0):.2%}"],
                    ["Max Score:", f"{summary_data.get('max_score', 0):.2%}"],
                ]

                summary_table = Table(summary_info, colWidths=[2*inch, 4.5*inch])
                summary_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))

                story.append(summary_table)
                story.append(Spacer(1, 0.2*inch))

            # Timeline chart
            try:
                chart_path = self._create_timeline_chart(timeline)
                if chart_path and Path(chart_path).exists():
                    story.append(Paragraph("Suspicious Segments", self.styles['Heading3']))
                    img = Image(chart_path, width=6*inch, height=2.4*inch)
                    story.append(img)
                    story.append(Spacer(1, 0.2*inch))
            except Exception as e:
                print(f"Warning: Skipping timeline chart: {e}")

            # Score distribution
            try:
                dist_path = self._create_score_distribution(timeline)
                if dist_path and Path(dist_path).exists():
                    story.append(Paragraph("Score Distribution", self.styles['Heading3']))
                    img = Image(dist_path, width=5*inch, height=2.5*inch)
                    story.append(img)
                    story.append(Spacer(1, 0.2*inch))
            except Exception as e:
                print(f"Warning: Skipping score distribution: {e}")

            # Segment details table
            segments = timeline.get("segments", [])
            if segments:
                story.append(PageBreak())
                story.append(Paragraph("Segment Details", self.styles['CustomSubtitle']))

                segment_data = [["Start", "End", "Duration", "Avg Score", "Frames"]]
                for seg in segments[:10]:  # Limit to first 10 segments
                    segment_data.append([
                        f"{seg['start_time']:.1f}s",
                        f"{seg['end_time']:.1f}s",
                        f"{seg['duration']:.1f}s",
                        f"{seg['avg_score']:.2%}",
                        str(seg['frame_count'])
                    ])

                seg_table = Table(segment_data, colWidths=[1*inch, 1*inch, 1*inch, 1.3*inch, 1*inch])
                seg_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]))

                story.append(seg_table)

        # TruFor forensic visualizations (if exists)
        try:
            heatmap_path = list(self.job_dir.glob("*_heatmap.png"))
            conf_path = list(self.job_dir.glob("*_conf.png"))
            noiseprint_path = list(self.job_dir.glob("*_noiseprint.png"))

            if heatmap_path or conf_path or noiseprint_path:
                story.append(PageBreak())
                story.append(Paragraph("Forensic Visualizations", self.styles['CustomSubtitle']))

                # Methodology explanation
                method_text = (
                    "The following heatmaps show pixel-level forensic analysis results. "
                    "<b>Red areas</b> indicate potential manipulation, while <b>blue/green areas</b> indicate authentic regions. "
                    "Confidence maps show the model's certainty in its predictions."
                )
                story.append(Paragraph(method_text, self.styles['Normal']))
                story.append(Spacer(1, 0.2*inch))

                # Anomaly heatmap
                if heatmap_path and heatmap_path[0].exists():
                    story.append(Paragraph("Anomaly Detection Heatmap", self.styles['Heading3']))
                    img = Image(str(heatmap_path[0]), width=5.5*inch, height=5.5*inch, kind='proportional')
                    story.append(img)
                    story.append(Paragraph(
                        "<i>This map highlights regions where the model detected anomalies or manipulations.</i>",
                        self.styles['Normal']
                    ))
                    story.append(Spacer(1, 0.3*inch))

                # Confidence map
                if conf_path and conf_path[0].exists():
                    story.append(Paragraph("Model Confidence Map", self.styles['Heading3']))
                    img = Image(str(conf_path[0]), width=5.5*inch, height=5.5*inch, kind='proportional')
                    story.append(img)
                    story.append(Paragraph(
                        "<i>This map shows the model's confidence level for each pixel. Higher values indicate greater certainty.</i>",
                        self.styles['Normal']
                    ))
                    story.append(Spacer(1, 0.3*inch))

                # Noiseprint++ map
                if noiseprint_path and noiseprint_path[0].exists():
                    story.append(Paragraph("Noiseprint++ Forensic Analysis", self.styles['Heading3']))
                    img = Image(str(noiseprint_path[0]), width=5.5*inch, height=5.5*inch, kind='proportional')
                    story.append(img)
                    story.append(Paragraph(
                        "<i>This visualization shows camera sensor noise patterns. Inconsistencies may indicate splicing or manipulation.</i>",
                        self.styles['Normal']
                    ))
                    story.append(Spacer(1, 0.2*inch))

        except Exception as e:
            print(f"Warning: Skipping forensic visualizations: {e}")

        # DeepfakeBench keyframes (if exists)
        try:
            keyframe_dir = self.job_dir / "keyframes"
            if keyframe_dir.exists() and detection_type == "deepfakebench":
                keyframe_files = sorted(list(keyframe_dir.glob("segment_*_keyframe.jpg")))

                if keyframe_files:
                    story.append(PageBreak())
                    story.append(Paragraph("Suspicious Segment Keyframes", self.styles['CustomSubtitle']))

                    keyframe_text = (
                        "The following images are keyframes extracted from the most suspicious segments of the video. "
                        "These frames had the highest detection scores."
                    )
                    story.append(Paragraph(keyframe_text, self.styles['Normal']))
                    story.append(Spacer(1, 0.2*inch))

                    # Display up to 6 keyframes in a 2-column layout
                    for i, keyframe_path in enumerate(keyframe_files[:6], 1):
                        if keyframe_path.exists():
                            story.append(Paragraph(f"Segment {i} Keyframe", self.styles['Heading3']))
                            img = Image(str(keyframe_path), width=4*inch, height=3*inch, kind='proportional')
                            story.append(img)
                            story.append(Spacer(1, 0.2*inch))

        except Exception as e:
            print(f"Warning: Skipping keyframes: {e}")

        # Footer
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(
            f"<i>Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>",
            self.styles['Normal']
        ))

        # Build PDF
        doc.build(story)

        return str(output_path)


def generate_pdf_report(job_id: str, job_dir: str, metadata: Dict) -> str:
    """
    Convenience function to generate PDF report

    Args:
        job_id: Job identifier
        job_dir: Path to job directory
        metadata: Job metadata and results

    Returns:
        Path to generated PDF file
    """
    generator = PDFReportGenerator(job_dir)
    return generator.generate_report(metadata)
