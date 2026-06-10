from __future__ import annotations


def _rows(text: str) -> list[list[str]]:
    return [[c.strip() for c in line.split('|')] for line in text.strip().splitlines() if line.strip() and not line.strip().startswith('#')]


def _tags(s: str) -> list[str]:
    return [x.strip() for x in s.split(',') if x.strip()]

SOURCE_TEXT = r'''
Lenny's Podcast|podcast|https://www.lennysnewsletter.com/|https://www.lennysnewsletter.com/feed|en|S|podcast,product,ai-products,startups
Peter Yang|newsletter|https://www.peterjyang.com/|https://www.peterjyang.com/feed|en|A|product,agents,creators
Every AI and I|newsletter|https://every.to/|https://every.to/feed.xml|en|A|ai-workflows,product,interview
Unsupervised Learning by Redpoint|podcast|https://www.redpoint.com/unsupervised-learning/||en|A|vc,ai-startups,interview
Training Data by Sequoia|podcast|https://www.sequoiacap.com/podcast/training-data/||en|A|vc,founders,ai-startups
Minus One by South Park Commons|podcast|https://www.southparkcommons.com/||en|A|frontier-tech,founders,ai
Google DeepMind Podcast|podcast|https://deepmind.google/discover/the-podcast/|https://deepmind.google/blog/rss.xml|en|S|deepmind,research,podcast
No Priors|podcast|https://www.nopriors.com/||en|S|ai-startups,models,interview
a16z AI|investor|https://a16z.com/ai/|https://a16z.com/feed/|en|S|vc,ai,infra
Latent Space|podcast|https://www.latent.space/|https://www.latent.space/feed|en|S|llm,agents,ai-engineering
The AI Daily Brief|podcast|https://www.aidailybrief.com/||en|A|daily-news,models,products
Y Combinator|youtube|https://www.youtube.com/@ycombinator||en|A|yc,startups,video
Lex Fridman Podcast|podcast|https://lexfridman.com/podcast/|https://lexfridman.com/feed/podcast/|en|S|interview,agi,research
Dwarkesh Podcast|podcast|https://www.dwarkeshpatel.com/|https://www.dwarkeshpatel.com/feed|en|S|agi,economics,interview
Hard Fork|podcast|https://www.nytimes.com/column/hard-fork|https://feeds.simplecast.com/l2i9YnTd|en|A|tech-media,ai,podcast
Big Technology Podcast|podcast|https://www.bigtechnology.com/|https://www.bigtechnology.com/feed|en|A|tech-media,ai,interview
The TED AI Show|podcast|https://www.ted.com/podcasts/the-ted-ai-show||en|B|ai,podcast
Eye on AI|podcast|https://www.eye-on.ai/||en|A|ai,research,interview
Practical AI|podcast|https://changelog.com/practicalai|https://changelog.com/practicalai/feed|en|A|ml,engineering,podcast
Cognitive Revolution|podcast|https://www.cognitiverevolution.ai/||en|A|agi,agents,podcast
Machine Learning Street Talk|youtube|https://www.youtube.com/@MachineLearningStreetTalk||en|A|ml,research,video
TWIML AI Podcast|podcast|https://twimlai.com/podcast/twimlai/|https://twimlai.com/feed/podcast/|en|A|ml,podcast,research
The Gradient Podcast|podcast|https://thegradient.pub/podcast/|https://thegradient.pub/rss/|en|A|research,podcast,ml
Data Exchange Podcast|podcast|https://gradientflow.com/podcast/||en|B|data,ml,podcast
NVIDIA AI Podcast|podcast|https://blogs.nvidia.com/ai-podcast/|https://blogs.nvidia.com/feed/|en|A|nvidia,chips,podcast
Microsoft Research Podcast|podcast|https://www.microsoft.com/en-us/research/podcast/|https://www.microsoft.com/en-us/research/feed/|en|B|research,podcast,microsoft
OpenAI News|company_blog|https://openai.com/news/|https://openai.com/news/rss.xml|en|S|openai,models,product
Anthropic News|company_blog|https://www.anthropic.com/news|https://www.anthropic.com/news/rss.xml|en|S|anthropic,claude,safety
Google DeepMind Blog|research_lab|https://deepmind.google/blog/|https://deepmind.google/blog/rss.xml|en|S|deepmind,research,gemini
Google AI Blog|company_blog|https://ai.googleblog.com/|https://ai.googleblog.com/feeds/posts/default|en|S|google,research,ai
Microsoft AI Blog|company_blog|https://blogs.microsoft.com/ai/|https://blogs.microsoft.com/ai/feed/|en|S|microsoft,copilot,enterprise
Meta AI Blog|company_blog|https://ai.meta.com/blog/||en|S|meta,llama,open-source
NVIDIA Blog AI|company_blog|https://blogs.nvidia.com/blog/category/deep-learning/|https://blogs.nvidia.com/feed/|en|S|nvidia,chips,ai
Hugging Face Blog|company_blog|https://huggingface.co/blog|https://huggingface.co/blog/feed.xml|en|S|open-source,models,developer
Mistral AI News|company_blog|https://mistral.ai/news/||en|S|mistral,models,open-source
Cohere Blog|company_blog|https://cohere.com/blog|https://cohere.com/blog/rss.xml|en|A|cohere,enterprise,models
Perplexity Blog|company_blog|https://www.perplexity.ai/hub/blog||en|A|search,consumer-ai
Runway Blog|company_blog|https://runwayml.com/research/||en|A|video,creative-ai,research
ElevenLabs Blog|company_blog|https://elevenlabs.io/blog||en|A|voice,audio,product
Stability AI News|company_blog|https://stability.ai/news||en|B|image,open-source
xAI News|company_blog|https://x.ai/news||en|A|xai,models,grok
Sakana AI Blog|research_lab|https://sakana.ai/blog/|https://sakana.ai/feed.xml|en|A|research,agents,japan
AI2 Blog|research_lab|https://allenai.org/blog|https://allenai.org/blog/rss.xml|en|A|research,open-source
Thinking Machines Lab|research_lab|https://thinkingmachines.ai/||en|A|research,frontier-lab
Cursor Blog|company_blog|https://www.cursor.com/blog||en|A|ai-coding,ide
Cognition Blog|company_blog|https://cognition.ai/blog||en|A|ai-coding,agents
Replit Blog|company_blog|https://blog.replit.com/|https://blog.replit.com/feed|en|A|ai-coding,developer
Lovable Blog|company_blog|https://lovable.dev/blog||en|A|ai-coding,app-builder
Vercel AI|company_blog|https://vercel.com/blog|https://vercel.com/atom|en|A|developer,ai-sdk
LangChain Blog|company_blog|https://blog.langchain.com/|https://blog.langchain.com/rss/|en|A|agents,framework
LlamaIndex Blog|company_blog|https://www.llamaindex.ai/blog|https://www.llamaindex.ai/blog/rss.xml|en|A|rag,agents,developer
Together AI Blog|company_blog|https://www.together.ai/blog|https://www.together.ai/blog/rss.xml|en|B|infra,models
Fireworks AI Blog|company_blog|https://fireworks.ai/blog||en|B|inference,infra
Groq Blog|company_blog|https://groq.com/blog/|https://groq.com/feed/|en|B|chips,inference
Cerebras Blog|company_blog|https://www.cerebras.ai/blog||en|B|chips,training
CoreWeave Blog|company_blog|https://www.coreweave.com/blog||en|B|cloud,gpu,infra
Databricks Blog AI|company_blog|https://www.databricks.com/blog/category/solutions/ai-and-machine-learning|https://www.databricks.com/feed|en|B|enterprise-ai,data
Snowflake Blog AI|company_blog|https://www.snowflake.com/blog/category/generative-ai/||en|B|enterprise-ai,data
Salesforce AI Blog|company_blog|https://www.salesforce.com/blog/category/artificial-intelligence/||en|B|enterprise-ai,crm
Adobe Firefly Blog|company_blog|https://blog.adobe.com/en/topics/artificial-intelligence||en|B|creative-ai,enterprise
Apple Machine Learning Research|research_lab|https://machinelearning.apple.com/|https://machinelearning.apple.com/rss.xml|en|A|apple,research,on-device
Amazon Science AI|research_lab|https://www.amazon.science/tag/artificial-intelligence|https://www.amazon.science/index.rss|en|B|amazon,research,cloud
Oracle AI|company_blog|https://www.oracle.com/artificial-intelligence/||en|C|enterprise-ai,cloud
Tesla AI|company_blog|https://www.tesla.com/AI||en|A|robotics,autonomy
Figure AI News|company_blog|https://www.figure.ai/news||en|A|robotics,humanoid
Physical Intelligence|research_lab|https://www.physicalintelligence.company/||en|A|robotics,foundation-models
Stanford HAI|research_lab|https://hai.stanford.edu/news|https://hai.stanford.edu/news/rss.xml|en|A|policy,research,stanford
MIT CSAIL|research_lab|https://www.csail.mit.edu/news|https://www.csail.mit.edu/rss.xml|en|A|research,mit,ai
Berkeley BAIR|research_lab|https://bair.berkeley.edu/blog/|https://bair.berkeley.edu/blog/feed.xml|en|A|research,berkeley,ml
CMU Machine Learning|research_lab|https://blog.ml.cmu.edu/|https://blog.ml.cmu.edu/feed/|en|B|research,ml
Cornell Tech|research_lab|https://tech.cornell.edu/news/||en|C|research,ai
Papers with Code|developer|https://paperswithcode.com/|https://paperswithcode.com/latest/rss|en|A|papers,benchmarks
Hugging Face Papers|developer|https://huggingface.co/papers||en|A|papers,models
Hugging Face Models|developer|https://huggingface.co/models||en|A|models,open-source
GitHub Trending Python|developer|https://github.com/trending/python?since=daily||en|B|github,open-source
GitHub Trending TypeScript|developer|https://github.com/trending/typescript?since=daily||en|B|github,developer
Reuters Technology|media|https://www.reuters.com/technology/|https://www.reutersagency.com/feed/?best-topics=tech&post_type=best|en|S|media,technology
Bloomberg Technology|media|https://www.bloomberg.com/technology||en|S|media,markets,technology,paywall
Financial Times Tech|media|https://www.ft.com/technology||en|S|media,paywall,technology
Wall Street Journal Tech|media|https://www.wsj.com/tech||en|S|media,paywall,technology
New York Times Technology|media|https://www.nytimes.com/section/technology||en|S|media,technology
Washington Post Technology|media|https://www.washingtonpost.com/technology/||en|A|media,technology
The Economist Technology Quarterly|media|https://www.economist.com/technology-quarterly||en|A|media,paywall
The Atlantic Technology|media|https://www.theatlantic.com/technology/||en|B|media,analysis
TIME AI|media|https://time.com/collection/time100-ai/||en|B|media,ai
Fortune AI|media|https://fortune.com/tag/artificial-intelligence/||en|B|media,business
Forbes AI|media|https://www.forbes.com/ai/||en|B|media,business
CNBC Tech|media|https://www.cnbc.com/technology/|https://www.cnbc.com/id/19854910/device/rss/rss.html|en|A|media,business
BBC Technology|media|https://www.bbc.com/news/technology|https://feeds.bbci.co.uk/news/technology/rss.xml|en|A|media,technology
The Guardian Technology|media|https://www.theguardian.com/technology/artificialintelligenceai|https://www.theguardian.com/technology/artificialintelligenceai/rss|en|A|media,ai
AP Technology|media|https://apnews.com/hub/technology||en|A|media,technology
The Verge AI|media|https://www.theverge.com/ai-artificial-intelligence|https://www.theverge.com/rss/ai-artificial-intelligence/index.xml|en|A|media,consumer-ai
WIRED AI|media|https://www.wired.com/tag/artificial-intelligence/|https://www.wired.com/feed/tag/ai/latest/rss|en|A|media,ai
MIT Technology Review AI|media|https://www.technologyreview.com/topic/artificial-intelligence/|https://www.technologyreview.com/feed/|en|A|media,research
TechCrunch AI|media|https://techcrunch.com/category/artificial-intelligence/|https://techcrunch.com/category/artificial-intelligence/feed/|en|A|media,startups
The Information AI|media|https://www.theinformation.com/tag/ai||en|A|media,paywall,startups
Semafor Tech|media|https://www.semafor.com/vertical/tech||en|B|media,tech
Axios AI|media|https://www.axios.com/technology/artificial-intelligence||en|B|media,policy
VentureBeat AI|media|https://venturebeat.com/category/ai/|https://venturebeat.com/category/ai/feed/|en|B|media,enterprise
Ars Technica AI|media|https://arstechnica.com/tag/ai/|https://feeds.arstechnica.com/arstechnica/index|en|B|media,technology
ZDNet AI|media|https://www.zdnet.com/topic/artificial-intelligence/||en|B|media,enterprise
The Register AI|media|https://www.theregister.com/software/ai_ml/|https://www.theregister.com/software/ai_ml/headlines.atom|en|B|media,enterprise
Engadget AI|media|https://www.engadget.com/tag/artificial-intelligence/||en|C|media,consumer
Tom's Hardware AI|media|https://www.tomshardware.com/tag/ai||en|C|media,hardware
9to5Google AI|media|https://9to5google.com/guides/ai/||en|C|media,google
Windows Central AI|media|https://www.windowscentral.com/tag/artificial-intelligence||en|C|media,microsoft
Android Authority AI|media|https://www.androidauthority.com/artificial-intelligence/||en|C|media,android
MacRumors AI|media|https://www.macrumors.com/guide/apple-intelligence/||en|C|media,apple
Import AI|newsletter|https://importai.substack.com/|https://importai.substack.com/feed|en|A|newsletter,research,policy
The Batch|newsletter|https://www.deeplearning.ai/the-batch/|https://www.deeplearning.ai/the-batch/feed/|en|A|newsletter,ai
Ben's Bites|newsletter|https://www.bensbites.com/||en|B|newsletter,ai-news
TLDR AI|newsletter|https://tldr.tech/ai|https://tldr.tech/ai/rss|en|B|newsletter,ai-news
The Rundown AI|newsletter|https://www.therundown.ai/||en|B|newsletter,ai-news
The Decoder|media|https://the-decoder.com/|https://the-decoder.com/feed/|en|B|media,ai
AI Supremacy|newsletter|https://aisupremacy.substack.com/|https://aisupremacy.substack.com/feed|en|C|newsletter,ai
The Neuron|newsletter|https://www.theneurondaily.com/||en|C|newsletter,ai
Stratechery|newsletter|https://stratechery.com/|https://stratechery.com/feed/|en|A|analysis,platforms,paywall
Platformer|newsletter|https://www.platformer.news/|https://www.platformer.news/feed|en|A|media,platforms
One Useful Thing|newsletter|https://www.oneusefulthing.org/|https://www.oneusefulthing.org/feed|en|A|ai-work,education
Simon Willison Weblog|blog|https://simonwillison.net/|https://simonwillison.net/atom/everything/|en|A|developer,llm
Interconnects|newsletter|https://www.interconnects.ai/|https://www.interconnects.ai/feed|en|A|open-models,research
AI Snake Oil|newsletter|https://www.aisnakeoil.com/|https://www.aisnakeoil.com/feed|en|A|policy,ai-risk
Eugene Yan Blog|blog|https://eugeneyan.com/|https://eugeneyan.com/rss/|en|B|ml,engineering
Chip Huyen Blog|blog|https://huyenchip.com/blog/|https://huyenchip.com/feed.xml|en|B|ml,engineering
Lilian Weng Blog|blog|https://lilianweng.github.io/|https://lilianweng.github.io/index.xml|en|A|research,agents
Sebastian Raschka Blog|blog|https://sebastianraschka.com/blog/|https://sebastianraschka.com/rss_feed.xml|en|B|ml,education
Jay Alammar Blog|blog|https://jalammar.github.io/|https://jalammar.github.io/feed.xml|en|B|visual-explainers,llm
机器之心|media|https://www.jiqizhixin.com/||zh|A|中文,AI,媒体
量子位|media|https://www.qbitai.com/||zh|A|中文,AI,媒体
甲子光年|media|https://www.jazzyear.com/||zh|B|中文,产业,AI
36氪 AI|media|https://36kr.com/search/articles/人工智能||zh|B|中文,创业,AI
晚点 LatePost AI|media|https://www.latepost.com/||zh|A|中文,商业,AI
腾讯科技 AI|media|https://new.qq.com/ch/tech/||zh|B|中文,科技
界面新闻 AI|media|https://www.jiemian.com/||zh|B|中文,商业
澎湃新闻 AI|media|https://www.thepaper.cn/||zh|C|中文,新闻
财新 AI|media|https://www.caixin.com/technology/||zh|A|中文,商业,paywall
虎嗅 AI|media|https://www.huxiu.com/||zh|B|中文,商业
极客公园 AI|media|https://www.geekpark.net/||zh|B|中文,产品
Founder Park AI|media|https://www.founderpark.com/||zh|B|中文,创业
硅星人 AI|media|https://www.guixingren.com/||zh|C|中文,硅谷
InfoQ 中文 AI|media|https://www.infoq.cn/topic/AI|https://www.infoq.cn/feed.xml|zh|B|中文,开发者
'''

X_ACCOUNTS = 'sama,gdb,ilyasut,DarioAmodei,demishassabis,JeffDean,NoamShazeer,sundarpichai,satyanadella,kevin_scott,mustafasuleyman,ylecun,jensenhuang,elonmusk,karpathy,AndrewYNg,ClementDelangue,arthurmensch,aidangomez,AravSrinivas,natfriedman,danielgross,btaylor,fchollet,JimFan,hwchase17,jeremyphoward,RichardSocher,sarahguo,eladgil,a16z,sequoia,ycombinator,swyx,latentspacepod,dwarkesh_sp,lexfridman,KevinRoose,CaseyNewton,benedictevans'

PEOPLE_TEXT = r'''
Sam Altman|萨姆·奥特曼|CEO|OpenAI|models,executive,openai
Greg Brockman|格雷格·布罗克曼|President|OpenAI|openai,executive
Brad Lightcap|布拉德·莱特卡普|COO|OpenAI|openai,business
Mira Murati|米拉·穆拉蒂|Founder / former CTO|Thinking Machines Lab|frontier-lab,models
Ilya Sutskever|伊利亚·苏茨克维|Founder|Safe Superintelligence|safety,research
Dario Amodei|达里奥·阿莫迪|CEO|Anthropic|anthropic,claude,safety
Daniela Amodei|丹妮拉·阿莫迪|President|Anthropic|anthropic,executive
Demis Hassabis|戴密斯·哈萨比斯|CEO|Google DeepMind|deepmind,research
Jeff Dean|杰夫·迪恩|Chief Scientist|Google DeepMind / Google Research|google,research
Noam Shazeer|诺姆·沙泽尔|AI leader|Google|models,research
Sundar Pichai|桑达尔·皮查伊|CEO|Google / Alphabet|google,executive
Satya Nadella|萨提亚·纳德拉|CEO|Microsoft|microsoft,executive
Kevin Scott|凯文·斯科特|CTO|Microsoft|microsoft,ai
Mustafa Suleyman|穆斯塔法·苏莱曼|CEO Microsoft AI|Microsoft AI|microsoft,ai
Mark Zuckerberg|马克·扎克伯格|CEO|Meta|meta,llama
Yann LeCun|杨立昆|Chief AI Scientist|Meta AI|research,open-source
Joelle Pineau|若埃尔·皮诺|AI executive|Meta AI|research
Jensen Huang|黄仁勋|CEO|NVIDIA|chips,gpu
Elon Musk|埃隆·马斯克|Founder|xAI / Tesla|xai,tesla
Andrej Karpathy|安德烈·卡帕西|AI researcher|Independent|ai-education,agents
Fei-Fei Li|李飞飞|Professor / Founder|Stanford / World Labs|research,spatial-ai
Andrew Ng|吴恩达|Founder|DeepLearning.AI|education,ml
Clem Delangue|克莱姆·德朗格|CEO|Hugging Face|open-source
Arthur Mensch|阿蒂尔·门施|CEO|Mistral AI|mistral,models
Aidan Gomez|艾丹·戈麦斯|CEO|Cohere|cohere,models
Emad Mostaque|艾马德·莫斯塔克|Founder|Stability AI|image,open-source
Alexandr Wang|亚历山大·王|Founder|Scale AI|data,infra
Aravind Srinivas|阿拉文德·斯里尼瓦斯|CEO|Perplexity|search,consumer-ai
Brett Adcock|布雷特·阿德科克|Founder|Figure AI|robotics
Richard Socher|理查德·索彻|CEO|You.com|search,ai
Cristobal Valenzuela|克里斯托瓦尔·瓦伦苏埃拉|CEO|Runway|video,creative-ai
David Holz|大卫·霍尔兹|Founder|Midjourney|image,creative-ai
Nat Friedman|纳特·弗里德曼|Investor / Builder|Independent|investor,developer
Daniel Gross|丹尼尔·格罗斯|Investor / Founder|Independent|investor,ai
Bret Taylor|布雷特·泰勒|Chair / CEO|OpenAI / Sierra|agents,enterprise
Clay Bavor|克莱·巴沃|Founder|Sierra|agents,enterprise
Lin Qiao|乔林|CEO|Fireworks AI|infra,inference
Percy Liang|梁鹏|Professor|Stanford|research,foundation-models
Ion Stoica|伊恩·斯托伊卡|Professor / Founder|UC Berkeley / Anyscale|systems,ai
Pieter Abbeel|彼得·阿比尔|Professor / Founder|UC Berkeley / Covariant|robotics,research
Chelsea Finn|切尔西·芬恩|Professor|Stanford|robotics,research
Francois Chollet|弗朗索瓦·肖莱|Researcher|Google / ARC|reasoning,research
Jim Fan|吉姆·范|Researcher|NVIDIA|agents,robotics
Harrison Chase|哈里森·蔡斯|CEO|LangChain|agents,developer
Jerry Liu|刘杰瑞|CEO|LlamaIndex|rag,developer
Soumith Chintala|苏米特·钦塔拉|AI engineer|Meta / PyTorch|open-source
Thomas Wolf|托马斯·沃尔夫|Co-founder|Hugging Face|open-source
Jeremy Howard|杰里米·霍华德|Founder|fast.ai|education,ml
Sebastian Thrun|塞巴斯蒂安·特龙|Founder|Udacity|autonomy,education
Kai-Fu Lee|李开复|Investor / CEO|Sinovation Ventures / 01.AI|china,models
Richard Sutton|理查德·萨顿|Researcher|University of Alberta|reinforcement-learning
Geoffrey Hinton|杰弗里·辛顿|Researcher|University of Toronto|deep-learning,safety
Yoshua Bengio|约书亚·本吉奥|Researcher|Mila|deep-learning,safety
Stuart Russell|斯图尔特·罗素|Professor|UC Berkeley|ai-safety
Marc Andreessen|马克·安德森|Co-founder|a16z|vc,platforms
Ben Horowitz|本·霍洛维茨|Co-founder|a16z|vc,startups
Martin Casado|马丁·卡萨多|General Partner|a16z|infra,vc
Sarah Guo|莎拉·郭|Founder|Conviction|vc,ai
Elad Gil|埃拉德·吉尔|Investor|Independent|vc,ai
Sonya Huang|索尼娅·黄|Investor|Sequoia|vc,ai
Pat Grady|帕特·格雷迪|Partner|Sequoia|vc
Alfred Lin|林君睿|Partner|Sequoia|vc
Andrew Chen|安德鲁·陈|Partner|a16z|growth,vc
Anjney Midha|安杰尼·米达|Partner|a16z|ai,vc
Justine Moore|贾斯汀·穆尔|Partner|a16z|consumer-ai,vc
Garry Tan|盖瑞·谭|CEO|Y Combinator|startups,vc
Paul Graham|保罗·格雷厄姆|Co-founder|Y Combinator|startups,essays
Jared Friedman|贾里德·弗里德曼|Partner|Y Combinator|startups
Michael Seibel|迈克尔·塞贝尔|Partner|Y Combinator|startups
Lenny Rachitsky|莱尼·拉奇茨基|Host|Lenny's Podcast|product,podcast
Peter Yang|彼得·杨|Writer|Peter Yang|product,agents
Dan Shipper|丹·希珀|CEO|Every|ai-workflows
Swyx|Swyx|Host / Engineer|Latent Space|developer,llm
Alessio Fanelli|阿莱西奥·法内利|Host|Latent Space|developer,llm
Nathan Labenz|内森·拉本茨|Host|Cognitive Revolution|podcast,agi
Dwarkesh Patel|德瓦克什·帕特尔|Host|Dwarkesh Podcast|podcast,agi
Lex Fridman|莱克斯·弗里德曼|Host|Lex Fridman Podcast|podcast,interview
Ben Thompson|本·汤普森|Analyst|Stratechery|analysis,platforms
Casey Newton|凯西·牛顿|Journalist|Platformer / Hard Fork|media,platforms
Kevin Roose|凯文·鲁斯|Journalist|The New York Times / Hard Fork|media,ai
Ezra Klein|埃兹拉·克莱因|Journalist|The New York Times|media,policy
Kara Swisher|卡拉·斯威舍|Journalist|On with Kara Swisher|media,tech
Guido Appenzeller|圭多·阿彭泽勒|Investor / Advisor|a16z|infra,vc
Ankit Gupta|安基特·古普塔|Founder|Factory|ai-coding,agents
Logan Kilpatrick|洛根·基尔帕特里克|Developer advocate|Google|developer,ai
Ethan Mollick|伊桑·莫利克|Professor / Writer|Wharton|ai-work,education
Nathan Lambert|内森·兰伯特|Researcher / Writer|AI2 / Interconnects|open-models,research
Simon Willison|西蒙·威利森|Developer / Writer|Independent|developer,llm
Lilian Weng|翁荔|Researcher / Writer|OpenAI|agents,research
'''

COMPANY_TEXT = r'''
OpenAI|company|https://openai.com/|models,chatgpt,api
Anthropic|company|https://www.anthropic.com/|claude,safety
Google DeepMind|research_lab|https://deepmind.google/|research,gemini
Google AI|company|https://ai.google/|research,products
Microsoft AI|company|https://www.microsoft.com/en-us/ai|copilot,enterprise
Meta AI|company|https://ai.meta.com/|llama,open-source
NVIDIA|company|https://www.nvidia.com/en-us/ai-data-science/|gpu,chips
xAI|company|https://x.ai/|grok,models
Perplexity|company|https://www.perplexity.ai/|search,consumer-ai
Mistral AI|company|https://mistral.ai/|models,open-source
Cohere|company|https://cohere.com/|enterprise,models
Hugging Face|company|https://huggingface.co/|open-source,models
Scale AI|company|https://scale.com/|data,infra
Character.AI|company|https://character.ai/|consumer-ai
Inflection AI|company|https://inflection.ai/|agents
Adept|company|https://www.adept.ai/|agents
Runway|company|https://runwayml.com/|video,creative-ai
Midjourney|company|https://www.midjourney.com/|image,creative-ai
ElevenLabs|company|https://elevenlabs.io/|voice,audio
Stability AI|company|https://stability.ai/|image,open-source
Cursor / Anysphere|company|https://www.cursor.com/|ai-coding,ide
Cognition|company|https://cognition.ai/|ai-coding,agents
Replit|company|https://replit.com/|developer,ai-coding
Lovable|company|https://lovable.dev/|app-builder,ai-coding
Vercel AI|company|https://sdk.vercel.ai/|developer,ai-sdk
LangChain|company|https://www.langchain.com/|agents,framework
LlamaIndex|company|https://www.llamaindex.ai/|rag,framework
Together AI|company|https://www.together.ai/|infra,models
Fireworks AI|company|https://fireworks.ai/|inference,infra
Groq|company|https://groq.com/|chips,inference
Cerebras|company|https://www.cerebras.ai/|chips,training
CoreWeave|company|https://www.coreweave.com/|cloud,gpu
Databricks|company|https://www.databricks.com/|data,enterprise-ai
Snowflake AI|company|https://www.snowflake.com/en/data-cloud/snowflake-ai/|data,enterprise-ai
Salesforce AI|company|https://www.salesforce.com/artificial-intelligence/|crm,enterprise-ai
Adobe AI|company|https://www.adobe.com/sensei.html|creative-ai
Apple AI|company|https://www.apple.com/apple-intelligence/|on-device,consumer-ai
Amazon AI|company|https://aws.amazon.com/ai/|cloud,ai
Oracle AI|company|https://www.oracle.com/artificial-intelligence/|cloud,enterprise
Tesla AI|company|https://www.tesla.com/AI|robotics,autonomy
Figure AI|company|https://www.figure.ai/|robotics,humanoid
Physical Intelligence|research_lab|https://www.physicalintelligence.company/|robotics,foundation-models
Sakana AI|research_lab|https://sakana.ai/|research,japan
AI2|research_lab|https://allenai.org/|research,open-source
Stanford HAI|institution|https://hai.stanford.edu/|research,policy
MIT CSAIL|institution|https://www.csail.mit.edu/|research,cs
Berkeley BAIR|institution|https://bair.berkeley.edu/|research,ml
Y Combinator|investor|https://www.ycombinator.com/|startups,vc
a16z|investor|https://a16z.com/ai/|vc,ai
Sequoia Capital|investor|https://www.sequoiacap.com/|vc,ai
Redpoint|investor|https://www.redpoint.com/|vc,ai
South Park Commons|community|https://www.southparkcommons.com/|community,frontier-tech
Conviction|investor|https://www.conviction.com/|vc,ai
Greylock|investor|https://greylock.com/|vc,ai
Lightspeed|investor|https://lsvp.com/|vc
General Catalyst|investor|https://www.generalcatalyst.com/|vc
Benchmark|investor|https://www.benchmark.com/|vc
The Information|media|https://www.theinformation.com/|media,paywall
Reuters|media|https://www.reuters.com/|media
Bloomberg|media|https://www.bloomberg.com/|media,paywall
Financial Times|media|https://www.ft.com/|media,paywall
TechCrunch|media|https://techcrunch.com/|media,startups
'''


def build_sources() -> list[dict]:
    out = []
    for name, typ, url, rss, lang, priority, tags in _rows(SOURCE_TEXT):
        out.append({
            'name': name,
            'type': typ,
            'url': url,
            'rss': rss or None,
            'language': lang,
            'priority': priority,
            'paywall': 'paywall' in tags.lower(),
            'fetch_method': 'rss' if rss else 'manual_or_html',
            'tags': _tags(tags),
            'last_fetched_at': None,
            'notes': 'Seed source. Prefer official RSS, podcast RSS or YouTube RSS. Do not bypass paywalls.'
        })
    for account in X_ACCOUNTS.split(','):
        out.append({
            'name': f'X @{account}',
            'type': 'x_account',
            'url': f'https://x.com/{account}',
            'rss': None,
            'language': 'en',
            'priority': 'A',
            'paywall': False,
            'fetch_method': 'x_optional',
            'tags': ['x', 'executive', 'optional'],
            'last_fetched_at': None,
            'notes': 'Optional X source. Requires future X API or stable public RSS bridge; absence must not fail the workflow.'
        })
    return out


def build_people() -> list[dict]:
    out = []
    for name, zh, role, org, tags in _rows(PEOPLE_TEXT):
        out.append({
            'name': name,
            'zh': zh,
            'role': role,
            'org': org,
            'x': None,
            'youtube_query': f'{name} AI interview',
            'podcast_query': f'{name} podcast AI',
            'media_query': f'{name} artificial intelligence',
            'importance': 'S' if any(k in tags for k in ['openai','anthropic','deepmind','nvidia','microsoft','google','meta']) else 'A',
            'tags': _tags(tags),
            'source_links': [],
            'notes': 'Seed person entity for news/entity matching.'
        })
    return out


def build_companies() -> list[dict]:
    out = []
    for name, typ, url, tags in _rows(COMPANY_TEXT):
        out.append({
            'name': name,
            'type': typ,
            'url': url,
            'importance': 'S' if name in ['OpenAI','Anthropic','Google DeepMind','Microsoft AI','Meta AI','NVIDIA','xAI','Mistral AI','Hugging Face'] else 'A',
            'tags': _tags(tags),
            'notes': 'Seed company/institution entity for source and news matching.'
        })
    return out
