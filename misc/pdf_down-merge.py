import asyncio
import aiohttp
import aiofiles
import fitz  # The PyMuPDF library
import os
import time

async def download_pdf_relentlessly(session, url, directory="downloads"):
    """
    Asynchronously downloads a PDF. It will retry forever until successful.
    """
    file_name = os.path.join(directory, url.split("/")[-1])
    attempt = 0
    while True:
        try:
            # Set a timeout for the request to avoid hanging indefinitely
            timeout = aiohttp.ClientTimeout(total=60)
            async with session.get(url, timeout=timeout) as response:
                # Raise an exception for bad status codes (4xx or 5xx)
                response.raise_for_status()
                # Open the file and write the content
                async with aiofiles.open(file_name, 'wb') as f:
                    await f.write(await response.read())
                print(f"✅ Successfully downloaded {os.path.basename(file_name)}")
                return file_name # Exit the loop and return the file path on success
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            attempt += 1
            # Calculate wait time: 2s, 4s, 8s, 16s, then capped at 30s
            wait_time = min(30, 2 ** attempt)
            print(f"❌ Download failed for {os.path.basename(file_name)}: {e}")
            print(f"⏳ Retrying in {wait_time} seconds... (Attempt {attempt})")
            await asyncio.sleep(wait_time)

async def download_all_pdfs(urls):
    """
    Downloads all PDFs from a list of URLs concurrently and reliably.
    """
    download_dir = "downloads"
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    # Use a TCPConnector with a sensible limit to avoid overwhelming the server
    connector = aiohttp.TCPConnector(limit=10)
    async with aiohttp.ClientSession(connector=connector) as session:
        # Create a list of download tasks
        tasks = [download_pdf_relentlessly(session, url, directory=download_dir) for url in urls]
        # Wait for all tasks to complete
        downloaded_files = await asyncio.gather(*tasks)
        return downloaded_files

def merge_pdfs_fast(pdf_list, output_filename="merged_document.pdf"):
    """
    Merges a list of PDF files into a single PDF using the high-speed PyMuPDF library.
    """
    print("\n🚀 Starting to merge PDFs with the high-speed PyMuPDF engine...")
    result_pdf = fitz.open() # Create a new, empty PDF for the result

    # Sort the list to ensure correct chapter order (e.g., keep201, keep202, ...)
    pdf_list.sort()

    total_pdfs = len(pdf_list)
    for i, pdf_path in enumerate(pdf_list):
        print(f"  📄 Merging {i + 1}/{total_pdfs}: {os.path.basename(pdf_path)}")
        try:
            with fitz.open(pdf_path) as src_pdf:
                result_pdf.insert_pdf(src_pdf)
        except Exception as e:
            print(f"  Could not merge {pdf_path}: {e}")

    print(f"\n✨ Writing final merged file to {output_filename}...")
    start_time = time.time()
    # Save the merged PDF with options to optimize size
    result_pdf.save(output_filename, garbage=4, deflate=True)
    result_pdf.close()
    end_time = time.time()

    print(f"✅ Successfully merged {total_pdfs} PDFs in {end_time - start_time:.2f} seconds.")

async def main():
    """
    Main function to orchestrate the downloading and merging.
    """
    base_url = "https://ncert.nic.in/textbook/pdf/kemh"
    # Generate all 18 PDF URLs from keep201.pdf to keep218.pdf
    pdf_urls = [f"{base_url}{i}.pdf" for i in range(101, 115)]
    total_files = len(pdf_urls)

    print(f"Starting reliable download of {total_files} PDF files...")
    # This function will not return until all downloads are complete
    downloaded_files = await download_all_pdfs(pdf_urls)

    # Proceed with merging
    if downloaded_files:
        merge_pdfs_fast(downloaded_files, "ncert_class_xi_math.pdf")

        # Optional: Clean up the individual downloaded files and directory
        print("\n🧹 Cleaning up individual PDF files...")
        for pdf_file in downloaded_files:
            try:
                os.remove(pdf_file)
            except OSError as e:
                print(f"Error removing file {pdf_file}: {e}")
        try:
            os.rmdir("downloads")
            print("✅ Cleanup complete.")
        except OSError as e:
            print(f"Error removing directory 'downloads': {e}")

if __name__ == "__main__":
    # This is the modern, recommended way to run an asyncio program
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")