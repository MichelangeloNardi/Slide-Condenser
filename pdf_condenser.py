import os
import cv2
import numpy as np
from pdf2image import convert_from_path
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
import tempfile
import sys

class PDFCondenser:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.temp_dir = tempfile.mkdtemp()
        
    def convert_pdf_to_images(self):
        """Convert PDF pages to images"""
        return convert_from_path(self.pdf_path)
    
    def preprocess_image(self, img):
        """Convert image to binary format using adaptive thresholding"""
        # Convert to numpy array and grayscale
        img_np = np.array(img)
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        
        # Apply adaptive thresholding to handle varying lighting conditions
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Remove small noise
        kernel = np.ones((3,3), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        return binary
    
    def calculate_similarity(self, img1, img2):
        """Calculate similarity between two slides using binary operations"""
        # Preprocess both images
        binary1 = self.preprocess_image(img1)
        binary2 = self.preprocess_image(img2)
        
        # Resize images to the same dimensions (use the smaller dimensions)
        height = min(binary1.shape[0], binary2.shape[0])
        width = min(binary1.shape[1], binary2.shape[1])
        
        binary1 = cv2.resize(binary1, (width, height))
        binary2 = cv2.resize(binary2, (width, height))
        
        # Compute the union of both images
        union = cv2.bitwise_or(binary1, binary2)
        
        # Compute the difference between the union and the second image
        diff = cv2.bitwise_xor(union, binary2)
        
        # Calculate the percentage of different pixels
        total_pixels = width * height
        different_pixels = np.count_nonzero(diff)
        similarity = 1 - (different_pixels / total_pixels)
        
        return similarity
    
    def find_similar_slides(self, images, threshold=0.99):
        """Find consecutive slides that are very similar"""
        similar_pairs = []
        for i in range(len(images) - 1):
            similarity = self.calculate_similarity(images[i], images[i + 1])
            print(f"Similarity between slide {i} and {i+1}: {similarity:.4f}")
            if similarity > threshold:
                similar_pairs.append((i, i + 1))
        return similar_pairs
    
    def merge_slides(self, pdf_path, output_path, similar_pairs):
        """Merge similar slides into a new PDF"""
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        
        # Create a set of slides to skip (second slides in similar pairs)
        slides_to_skip = {pair[0] for pair in similar_pairs}
        
        # Add slides to the new PDF, skipping similar ones
        for i in range(len(reader.pages)):
            if i not in slides_to_skip:
                writer.add_page(reader.pages[i])
        
        # Write the output PDF
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
    
    def process_pdf(self, output_path, similarity_threshold=0.99):
        """Main function to process the PDF"""
        # Convert PDF to images
        images = self.convert_pdf_to_images()
        
        # Find similar slides
        similar_pairs = self.find_similar_slides(images, similarity_threshold)
        
        # Merge slides and create new PDF
        self.merge_slides(self.pdf_path, output_path, similar_pairs)
        
        return len(similar_pairs)

def main():
    if len(sys.argv) != 3:
        print("Usage: python pdf_condenser.py <input_pdf> <output_pdf>")
        print("Example: python pdf_condenser.py presentation.pdf condensed_presentation.pdf")
        sys.exit(1)
        
    input_pdf = sys.argv[1]
    output_pdf = sys.argv[2]
    
    if not os.path.exists(input_pdf):
        print(f"Error: Input file '{input_pdf}' does not exist")
        sys.exit(1)
        
    try:
        condenser = PDFCondenser(input_pdf)
        num_merged = condenser.process_pdf(output_pdf)
        
        print(f"\nProcessing complete!")
        print(f"Successfully merged {num_merged} similar slides!")
        print(f"Input PDF: {input_pdf}")
        print(f"Output PDF: {output_pdf}")
        print(f"Original number of slides: {len(convert_from_path(input_pdf))}")
        print(f"New number of slides: {len(convert_from_path(output_pdf))}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 