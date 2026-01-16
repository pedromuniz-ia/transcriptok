import { VideoInput } from "../components/video-input";
import { TranscriptHistory } from "../components/transcript-history";

export default function Home() {
  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="hero-gradient py-16 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Cole o link do seu video aqui
          </h1>
          <p className="text-muted-foreground text-lg mb-8">
            Cole o link do TikTok, YouTube Shorts ou Instagram Reels para comecar.
          </p>
          <VideoInput />
        </div>
      </section>

      {/* History Section */}
      <section className="py-12 px-4">
        <div className="max-w-7xl mx-auto">
          <TranscriptHistory />
        </div>
      </section>
    </div>
  );
}
