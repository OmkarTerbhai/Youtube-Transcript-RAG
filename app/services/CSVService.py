import sys, re, subprocess, json
import pandas as pd
import os;
from datetime import datetime, timezone
from youtube_transcript_api import YouTubeTranscriptApi
from yt_dlp import YoutubeDL


WINDOW = 60      # seconds of transcript per row (your file looks ~60-70s)
STRIDE = 10      # new row every N seconds (your file looks ~10-15s)

class CSVService :

    def __init__(self):
        pass;

    def _video_id(self, url):
        m = re.search(r"(?:v=|youtu\.be/|shorts/)([\w-]{11})", url)
        return m.group(1) if m else url

    def _metadata(self, vid):
        opts = {"quiet": True, "skip_download": True}
        with YoutubeDL(opts) as ydl:
            j = ydl.extract_info(f"https://www.youtube.com/watch?v={vid}", download=False)
        d = j["upload_date"]  # YYYYMMDD
        published = datetime.strptime(d, "%Y%m%d").strftime("%Y-%m-%d 00:00:00 UTC")
        return j["channel_id"], j["title"], published

    def _transcript(self, vid):
        api = YouTubeTranscriptApi()
        snippets = api.fetch(vid, languages=["en"])
        return [{"text": s.text.replace("\n", " "), "start": s.start,
                 "end": s.start + s.duration} for s in snippets]

    def build_rows(self, url):
        vid = self._video_id(url)
        channel_id, title, published = self._metadata(vid)
        segs = self._transcript(vid)
        video_end = segs[-1]["end"]
        rows, t = [], 0.0
        while t < video_end:
            chunk = [s for s in segs if s["start"] >= t and s["start"] < t + WINDOW]
            if chunk:
                text = " ".join(s["text"] for s in chunk).strip()
                start, end = int(chunk[0]["start"]), int(chunk[-1]["end"])
                blob = {"channel_id": channel_id, "end": end, "published": published,
                        "start": start, "text": text, "title": title,
                        "url": f"https://youtu.be/{vid}"}
                rows.append({
                    "id": f"{vid}-t{chunk[0]['start']}",
                    "blob": str(blob),
                    "channel_id": channel_id,
                    "end": end,
                    "published": published,
                    "start": start,
                    "text": text,
                    "title": title,
                    "url": f"https://youtu.be/{vid}",
                })
            t += STRIDE

        cols = ["id", "blob", "channel_id", "end", "published", "start", "text", "title", "url"]
        out_path = r"..\..\data\youtube_gen.csv"  # change to any path you like
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        pd.DataFrame(rows, columns=cols).to_csv(out_path, index=False)
        print(f"Wrote {len(rows)} rows to {os.path.abspath(out_path)}")
        print(f"Wrote {len(rows)} rows");

        return rows