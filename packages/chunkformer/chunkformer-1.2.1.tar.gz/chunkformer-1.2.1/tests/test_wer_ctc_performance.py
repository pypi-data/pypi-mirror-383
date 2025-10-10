"""
Test WER performance on ChunkFormer model using audio_list.tsv data.
"""

import os
import subprocess
import tempfile
from pathlib import Path

import jiwer
import pandas as pd
import pytest

from chunkformer import ChunkFormerModel


class TestWERPerformance:
    """Test cases for WER performance evaluation."""

    @classmethod
    def setup_class(cls):
        """Set up test fixtures."""
        cls.model_name = "khanhld/chunkformer-ctc-large-vie"
        cls.model = ChunkFormerModel.from_pretrained(cls.model_name)
        cls.data_dir = Path(__file__).parent.parent
        cls.audio_list_path = cls.data_dir / "samples/data.tsv"

        # Load test data
        assert cls.audio_list_path.exists(), f"Audio list file not found: {cls.audio_list_path}"
        cls.test_data = pd.read_csv(cls.audio_list_path, sep="\t")

        # Validate test data structure
        required_columns = ["key", "wav", "txt"]
        for col in required_columns:
            assert col in cls.test_data.columns, f"Missing column: {col}"

        # Convert relative paths to absolute paths
        cls.test_data["audio_path"] = cls.test_data["wav"].apply(
            lambda x: str(cls.data_dir / x) if not os.path.isabs(x) else x
        )

        # Validate audio files exist
        missing_files = []
        for _, row in cls.test_data.iterrows():
            if not os.path.exists(row["audio_path"]):
                missing_files.append(row["audio_path"])

        if missing_files:
            print(f"Warning: Missing audio files: {missing_files}")
            # Filter out missing files for testing
            cls.test_data = cls.test_data[
                cls.test_data["audio_path"].apply(os.path.exists)
            ].reset_index(drop=True)

        assert len(cls.test_data) > 0, "No valid audio files found for testing"

    def test_endless_decode_wer_performance(self):
        """Test WER performance using endless_decode method."""
        predictions = []
        references = []

        for _, row in self.test_data.iterrows():
            audio_path = row["audio_path"]
            reference_text = row["txt"]

            try:
                # Perform endless decode
                result = self.model.endless_decode(
                    audio_path=audio_path,
                    chunk_size=64,
                    left_context_size=128,
                    right_context_size=128,
                    total_batch_duration=14400,
                    return_timestamps=False,
                )

                # Extract text from result
                if isinstance(result, dict) and "text" in result:
                    predicted_text = result["text"]
                elif isinstance(result, str):
                    predicted_text = result
                else:
                    predicted_text = str(result)
                predicted_text = predicted_text.strip()
                reference_text = reference_text.strip()
                predictions.append(predicted_text)
                references.append(reference_text)

                print(f"Audio {row['key']}: ")
                print(f"  Reference: {reference_text}")
                print(f"  Predicted: {predicted_text}")

            except Exception as e:
                pytest.fail(f"endless_decode failed for {audio_path}: {e}")

        # Calculate WER
        assert len(predictions) == len(references), "Mismatch in predictions and references"
        assert len(predictions) > 0, "No predictions generated"

        wer = jiwer.wer(references, predictions)

        print("\nEndless Decode Results:")
        print(f"Total samples: {len(predictions)}")
        print(f"WER: {wer:.4f} ({wer*100:.2f}%)")  # noqa: E231

        # Assert WER < 10%
        assert wer < 0.10, f"WER {wer:.4f} ({wer*100:.2f}%) exceeds 10% threshold"  # noqa: E231

    def test_batch_decode_wer_performance(self):
        """Test WER performance using batch_decode method."""
        audio_paths = self.test_data["audio_path"].tolist()
        references = self.test_data["txt"].tolist()

        try:
            # Perform batch decode
            predictions = self.model.batch_decode(
                audio_paths=audio_paths,
                chunk_size=64,
                left_context_size=128,
                right_context_size=128,
                total_batch_duration=14400,
            )

            # Ensure predictions is a list of strings
            if not isinstance(predictions, list):
                predictions = [predictions]

            # Clean predictions
            cleaned_predictions = []
            for pred in predictions:
                if isinstance(pred, dict) and "text" in pred:
                    cleaned_predictions.append(pred["text"].strip())
                elif isinstance(pred, str):
                    cleaned_predictions.append(pred.strip())
                else:
                    cleaned_predictions.append(str(pred).strip())

            predictions = cleaned_predictions

        except Exception as e:
            pytest.fail(f"batch_decode failed: {e}")

        # Validate results
        assert len(predictions) == len(
            references
        ), f"Mismatch: {len(predictions)} predictions vs {len(references)} references"
        assert len(predictions) > 0, "No predictions generated"

        # Print individual results
        for _, (ref, pred, key) in enumerate(zip(references, predictions, self.test_data["key"])):
            print(f"Audio {key}: ")
            print(f"  Reference: {ref}")
            print(f"  Predicted: {pred}")

        # Calculate WER
        wer = jiwer.wer(references, predictions)

        print("\nBatch Decode Results:")
        print(f"Total samples: {len(predictions)}")
        print(f"WER: {wer:.4f} ({wer*100:.2f}%)")  # noqa: E231

        # Assert WER < 10%
        assert wer < 0.10, f"WER {wer:.4f} ({wer*100:.2f}%) exceeds 10% threshold"  # noqa: E231

    def test_compare_decode_methods(self):
        """Compare WER performance between endless_decode and batch_decode."""
        # This test ensures both methods produce similar results
        audio_paths = self.test_data["audio_path"].tolist()
        references = self.test_data["txt"].tolist()

        # Get predictions from both methods
        endless_predictions = []
        for audio_path in audio_paths:
            try:
                result = self.model.endless_decode(
                    audio_path=audio_path,
                    chunk_size=64,
                    left_context_size=128,
                    right_context_size=128,
                    total_batch_duration=14400,
                    return_timestamps=False,
                )

                if isinstance(result, dict) and "text" in result:
                    text = result["text"]
                elif isinstance(result, str):
                    text = result
                else:
                    text = str(result)

                endless_predictions.append(text.strip())
            except Exception as e:
                pytest.fail(f"endless_decode failed: {e}")

        batch_predictions = self.model.batch_decode(
            audio_paths=audio_paths,
            chunk_size=64,
            left_context_size=128,
            right_context_size=128,
            total_batch_duration=14400,
        )

        # Clean batch predictions
        if not isinstance(batch_predictions, list):
            batch_predictions = [batch_predictions]

        cleaned_batch_predictions = []
        for pred in batch_predictions:
            if isinstance(pred, dict) and "text" in pred:
                cleaned_batch_predictions.append(pred["text"].strip())
            elif isinstance(pred, str):
                cleaned_batch_predictions.append(pred.strip())
            else:
                cleaned_batch_predictions.append(str(pred).strip())

        batch_predictions = cleaned_batch_predictions

        # Calculate WERs
        endless_wer = jiwer.wer(references, endless_predictions)
        batch_wer = jiwer.wer(references, batch_predictions)
        wer_diff = abs(endless_wer - batch_wer)

        print("\nComparison Results:")
        print(f"Endless decode WER: {endless_wer:.4f} ({endless_wer*100:.2f}%)")  # noqa: E231
        print(f"Batch decode WER: {batch_wer:.4f} ({batch_wer*100:.2f}%)")  # noqa: E231
        print(f"Difference: {wer_diff:.4f} ({batch_wer*100:.2f}%)")  # noqa: E231

        # Methods should produce reasonably similar results (within 5% difference)
        wer_diff = abs(endless_wer - batch_wer)
        assert (
            wer_diff < 0.01
        ), f"WER difference {wer_diff:.4f} between methods is too large"  # noqa: E231,E501

        # Calculate WERs
        wer = jiwer.wer(batch_predictions, endless_predictions)
        print(f"Mismatch WER: {wer:.4f} ({wer*100:.2f}%)")  # noqa: E231
        # Both methods should have WER < 10%
        assert wer < 0.01, f"Mismatch decode WER {wer:.4f} exceeds 5%"  # noqa: E231

    def test_command_line_batch_decode(self):
        """Test command line interface for batch transcription with WER calculation."""
        # Create a temporary TSV file with subset of test data
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tsv", delete=False) as temp_file:
            # Take first 3 samples for faster testing
            test_data = self.test_data.copy()

            # Prepare TSV content with required columns
            temp_file.write("key\twav\ttxt\n")
            for _, row in test_data.iterrows():
                temp_file.write(f"{row['key']}\t{row['audio_path']}\t{row['txt']}\n")

            temp_tsv_path = temp_file.name

        try:
            # Run chunkformer-decode command
            cmd = [
                "chunkformer-decode",
                "--model_checkpoint",
                self.model_name,
                "--audio_list",
                temp_tsv_path,
                "--total_batch_duration",
                "14400",
                "--chunk_size",
                "64",
                "--left_context_size",
                "128",
                "--right_context_size",
                "128",
            ]

            # Execute command and capture output
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=300  # 5 minute timeout
            )

            # Check if command executed successfully
            assert (
                result.returncode == 0
            ), f"Command failed with return code {result.returncode}. stderr: {result.stderr}"

            # Parse WER from output
            output_lines = result.stdout.strip().split("\n")
            wer_line = None
            for line in output_lines:
                if "Word Error Rate (WER):" in line:
                    wer_line = line
                    break

            assert wer_line is not None, f"WER not found in output: {result.stdout}"

            # Extract WER value
            wer_str = wer_line.split("Word Error Rate (WER):")[1].strip()
            wer_value = float(wer_str)

            print("\nCommand Line Batch Decode Results:")
            print(f"WER: {wer_value:.4f} ({wer_value*100:.2f}%)")  # noqa: E231

            # Assert WER < 10%
            assert (
                wer_value < 0.10
            ), f"Command line WER {wer_value:.4f} ({wer_value*100:.2f}%) exceeds 10% threshold"

            # Verify the output TSV file was updated with predictions
            updated_data = pd.read_csv(temp_tsv_path, sep="\t")
            assert "decode" in updated_data.columns, "decode column not found in output file"

        except subprocess.TimeoutExpired:
            pytest.fail("Command line test timed out after 5 minutes")
        except FileNotFoundError:
            pytest.skip("chunkformer-decode command not found in PATH")
        finally:
            # Clean up temporary file
            if os.path.exists(temp_tsv_path):
                os.unlink(temp_tsv_path)

    def test_command_line_long_form_audio(self):
        """Test command line interface for long-form audio transcription."""
        # Use the first audio file for long-form testing
        if len(self.test_data) == 0:
            pytest.skip("No test audio files available")

        test_audio_path = self.test_data.iloc[0]["audio_path"]

        try:
            # Run chunkformer-decode command for long-form audio
            cmd = [
                "chunkformer-decode",
                "--model_checkpoint",
                self.model_name,
                "--long_form_audio",
                test_audio_path,
                "--total_batch_duration",
                "14400",
                "--chunk_size",
                "64",
                "--left_context_size",
                "128",
                "--right_context_size",
                "128",
            ]

            # Execute command and capture output
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=120  # 2 minute timeout for single file
            )

            # Check if command executed successfully
            assert (
                result.returncode == 0
            ), f"Command failed with return code {result.returncode}. stderr: {result.stderr}"

            # Verify output contains transcription
            output_lines = result.stdout.strip().split("\n")
            assert len(output_lines) > 0, "No output generated"

            # Just verify that the model produces text output (find transcription lines)
            transcription_found = False
            transcription_text = ""
            for line in output_lines:
                # Look for lines with timestamp format HH:MM:SS:mmm - HH:MM:SS:mmm: text
                if " - " in line and ": " in line and not line.startswith("  "):
                    # Check if line has time format (digits and colons)
                    parts = line.split(": ", 1)
                    if len(parts) == 2:
                        timestamp_part = parts[0]
                        text_part = parts[1].strip()
                        if ":" in timestamp_part and text_part:
                            transcription_found = True
                            transcription_text = text_part
                            break

            assert transcription_found, f"No transcription text found in output: {result.stdout}"
            assert len(transcription_text) > 0, "Transcription text is empty"

            print("\nCommand Line Long-Form Audio Results:")
            print("Output:\n")
            for line in output_lines:
                print(f"  {line}")

        except subprocess.TimeoutExpired:
            pytest.fail("Long-form audio command line test timed out after 2 minutes")
        except FileNotFoundError:
            pytest.skip("chunkformer-decode command not found in PATH")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
