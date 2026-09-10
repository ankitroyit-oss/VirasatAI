/* =============================================
   VirasatAI — Monument Reviews & Ratings Data Layer
   Manages visitor feedback, 1-5 star ratings,
   local storage persistence, and dynamic statistics.
   ============================================= */

// Authentic baseline reviews for all 20 heritage sites
const SEED_REVIEWS = {
  "taj-mahal": [
    {
      id: "tm-1",
      author: "Aarav Sharma",
      rating: 5,
      date: "Aug 28, 2026",
      text: "Viewing the Taj Mahal at sunrise is an unforgettable experience. The translucent white Makrana marble seems to change hue with the morning light. Truly a timeless wonder of India!"
    },
    {
      id: "tm-2",
      author: "Priya Venkatesh",
      rating: 5,
      date: "Aug 14, 2026",
      text: "The intricate pietra dura marble inlay craftsmanship is mind-boggling up close. The symmetry and lush Charbagh gardens create sheer poetry in stone."
    },
    {
      id: "tm-3",
      author: "David Miller",
      rating: 5,
      date: "Jul 22, 2026",
      text: "One of the most magnificent architectural masterworks on earth. The acoustic resonance inside the central dome is deeply spiritual."
    },
    {
      id: "tm-4",
      author: "Meera Sen",
      rating: 4,
      date: "Jul 05, 2026",
      text: "Pure architectural perfection. Highly recommend taking an evening boat ride across the Yamuna for Mehtab Bagh reflections."
    }
  ],
  "red-fort": [
    {
      id: "rf-1",
      author: "Kabir Malhotra",
      rating: 5,
      date: "Sep 01, 2026",
      text: "Walking through Lahori Gate gave me goosebumps. The sheer scale of the red sandstone bastions and Diwan-i-Khas is breathtaking."
    },
    {
      id: "rf-2",
      author: "Siddharth Jain",
      rating: 4,
      date: "Aug 19, 2026",
      text: "Rich Mughal history right in the heart of Old Delhi. The evening sound and light show vividly brings Shah Jahan's empire to life."
    },
    {
      id: "rf-3",
      author: "Elena Rostova",
      rating: 5,
      date: "Jul 30, 2026",
      text: "The marble pillars and inlaid floral designs of Diwan-i-Aam are stunning. Incredible feeling standing where India celebrates Independence Day."
    }
  ],
  "qutb-minar": [
    {
      id: "qm-1",
      author: "Rohan Mukherjee",
      rating: 5,
      date: "Aug 25, 2026",
      text: "Standing beneath the 73-meter fluted minaret makes you marvel at 12th-century engineering. The calligraphy carved in red sandstone is sublime."
    },
    {
      id: "qm-2",
      author: "Ananya Deshmukh",
      rating: 5,
      date: "Aug 10, 2026",
      text: "The 1,600-year-old rust-resistant iron pillar in the courtyard is an ancient metallurgical marvel. A must-visit archaeological complex!"
    },
    {
      id: "qm-3",
      author: "Tariq Khan",
      rating: 4,
      date: "Jul 18, 2026",
      text: "Serene ruins, magnificent Afghan-style balconies, and lush green lawns. Perfect spot for photography and history enthusiasts."
    }
  ],
  "hawa-mahal": [
    {
      id: "hm-1",
      author: "Tanvi Rathore",
      rating: 5,
      date: "Aug 31, 2026",
      text: "The 953 jharokhas create a natural air-conditioning effect that works even during peak summer! The honeycomb pink sandstone facade is iconic."
    },
    {
      id: "hm-2",
      author: "Arjun Verma",
      rating: 4,
      date: "Aug 15, 2026",
      text: "Great rooftop cafes across the street offer the best panoramic views of the palace facade. Inside, the stained glass windows cast colorful patterns."
    },
    {
      id: "hm-3",
      author: "Sophie Laurent",
      rating: 5,
      date: "Jul 28, 2026",
      text: "A poetic tribute to Lord Krishna's crown. The narrow passages and cooling breeze give an authentic feel of Rajput royal life."
    }
  ],
  "amber-fort": [
    {
      id: "af-1",
      author: "Vikramaditya Singh",
      rating: 5,
      date: "Sep 03, 2026",
      text: "Sheesh Mahal (Palace of Mirrors) is out of this world! Lighting a single candle illuminates the entire ceiling in a galaxy of stars."
    },
    {
      id: "af-2",
      author: "Nisha Patel",
      rating: 5,
      date: "Aug 20, 2026",
      text: "Perched majestically atop the Cheel ka Teela hill with Maota Lake reflections. The blend of Hindu and Rajput artistic elements is unparalleled."
    },
    {
      id: "af-3",
      author: "Rajesh Kulkarni",
      rating: 4,
      date: "Jul 12, 2026",
      text: "Expansive courtyards, secret tunnels connecting to Jaigarh Fort, and brilliant elephant ride access paths. Splendid preservation."
    }
  ],
  "khajuraho": [
    {
      id: "kj-1",
      author: "Devendra Joshi",
      rating: 5,
      date: "Aug 22, 2026",
      text: "Kandariya Mahadeva temple is a triumph of Nagara architecture. The intricate stone friezes celebrating all aspects of human life and spirituality are sublime."
    },
    {
      id: "kj-2",
      author: "Dr. Alok Nath",
      rating: 5,
      date: "Aug 02, 2026",
      text: "Beyond the famous erotic sculptures, the celestial dancers (apsaras), musicians, and philosophical reliefs showcase medieval India's artistic zenith."
    },
    {
      id: "kj-3",
      author: "Claire Dupont",
      rating: 5,
      date: "Jun 29, 2026",
      text: "Peaceful atmosphere, manicured gardens, and breathtaking sandstone relief work. The evening light and sound show is deeply informative."
    }
  ],
  "konark-sun-temple": [
    {
      id: "ks-1",
      author: "Soumya Ranjan Das",
      rating: 5,
      date: "Sep 04, 2026",
      text: "The 24 colossal chariot wheels carved as accurate sundials showcase ancient Indian astronomical genius. The Kalinga architectural style is majestic!"
    },
    {
      id: "ks-2",
      author: "Debolina Banerjee",
      rating: 5,
      date: "Aug 17, 2026",
      text: "Watching the first rays of the sun strike the temple sanctum near Chandrabhaga beach is a mystical encounter with Odisha's sacred heritage."
    },
    {
      id: "ks-3",
      author: "Markus Weber",
      rating: 4,
      date: "Jul 25, 2026",
      text: "The monolithic war elephants and galloping horses carved from chlorite stone retain extraordinary expression after 800 years."
    }
  ],
  "hampi": [
    {
      id: "hp-1",
      author: "Girish Kulkarni",
      rating: 5,
      date: "Aug 29, 2026",
      text: "The stone chariot at Vijaya Vittala temple and musical pillars that resonate at different acoustic frequencies prove the grandeur of the Vijayanagara Empire."
    },
    {
      id: "hp-2",
      author: "Aishwarya Rao",
      rating: 5,
      date: "Aug 12, 2026",
      text: "Bouldered landscapes set against the Tungabhadra River, Virupaksha temple's living worship, and ruins stretching for miles. An open-air museum like no other."
    },
    {
      id: "hp-3",
      author: "Liam O'Connor",
      rating: 5,
      date: "Jul 15, 2026",
      text: "Rent a bicycle and spend at least two days exploring. The sunsets from Matanga Hill overlooking the ancient royal center are breathtaking."
    }
  ],
  "ajanta-caves": [
    {
      id: "aj-1",
      author: "Dr. Suniti Patil",
      rating: 5,
      date: "Sep 02, 2026",
      text: "The Padmapani and Vajrapani frescoes in Cave 1 retain luminous natural mineral pigments after 1,500 years. The spiritual calmness in the eyes is hypnotic."
    },
    {
      id: "aj-2",
      author: "Pranav Iyer",
      rating: 5,
      date: "Aug 16, 2026",
      text: "Chiseled into a horseshoe-shaped gorge over the Waghur river. The chaitya halls with arched vaulted roofs demonstrate peerless rock-cut architecture."
    },
    {
      id: "aj-3",
      author: "Haruto Sato",
      rating: 5,
      date: "Jul 20, 2026",
      text: "An unparalleled sanctuary of Mahayana Buddhist art. The stories from Jataka tales carved into every basalt surface left me in awe."
    }
  ],
  "ellora-caves": [
    {
      id: "el-1",
      author: "Kavita Bhonsle",
      rating: 5,
      date: "Aug 27, 2026",
      text: "Kailash Temple (Cave 16) is the greatest monolithic wonder of mankind. Carving 200,000 tonnes of basalt from top to bottom with chisels and hammers is superhuman!"
    },
    {
      id: "el-2",
      author: "Mohit Chawla",
      rating: 5,
      date: "Aug 09, 2026",
      text: "The harmonious coexistence of Buddhist, Hindu, and Jain cave temples side-by-side demonstrates ancient India's deep pluralistic ethos."
    },
    {
      id: "el-3",
      author: "Anna Schmidt",
      rating: 5,
      date: "Jul 11, 2026",
      text: "Words cannot do justice to Cave 16. It feels impossible that ancient Rashtrakuta artisans excavated a multi-story palace temple from a single rock."
    }
  ],
  "meenakshi-temple": [
    {
      id: "mt-1",
      author: "Senthil Kumar",
      rating: 5,
      date: "Sep 05, 2026",
      text: "The 14 towering gopurams decorated with thousands of vividly colored deities dominate the Madurai skyline. The 1,000-pillar hall is an acoustic triumph."
    },
    {
      id: "mt-2",
      author: "Lakshmi Sundaram",
      rating: 5,
      date: "Aug 21, 2026",
      text: "The vibrant spiritual energy during the evening palliarai ceremony is divine. The golden lotus tank (Potramarai Kulam) reflections are mesmerizing."
    },
    {
      id: "mt-3",
      author: "Michael Chang",
      rating: 5,
      date: "Jul 29, 2026",
      text: "A living temple vibrating with 2,500 years of unbroken devotion, temple bells, and timeless Dravidian sculpture."
    }
  ],
  "golden-temple": [
    {
      id: "gt-1",
      author: "Harpreet Singh",
      rating: 5,
      date: "Sep 06, 2026",
      text: "Harmandir Sahib illuminated with gold foil across the Amrit Sarovar holy pool radiates supreme peace. The Guru ka Langar feeding 100,000 people daily embodies selfless service."
    },
    {
      id: "gt-2",
      author: "Gurkirat Kaur",
      rating: 5,
      date: "Aug 18, 2026",
      text: "The soothing Gurbani kirtan echoing across the water soothes the soul. Entering through the four open doors welcoming all faiths is truly moving."
    },
    {
      id: "gt-3",
      author: "Robert Evans",
      rating: 5,
      date: "Jul 26, 2026",
      text: "The most welcoming sacred sanctuary I have ever visited worldwide. The volunteers and atmosphere of communal harmony are unforgettable."
    }
  ],
  "mysore-palace": [
    {
      id: "mp-1",
      author: "Karthik Wodeyar",
      rating: 5,
      date: "Sep 02, 2026",
      text: "When 97,000 incandescent bulbs illuminate Mysore Palace on Sunday evening, it looks like a scene straight out of a fairy tale! Indo-Saracenic grandeur at its finest."
    },
    {
      id: "mp-2",
      author: "Shruti Hegde",
      rating: 5,
      date: "Aug 11, 2026",
      text: "The Durbar Hall ceiling with Scottish stained glass, mahogany carvings, and solid silver doors showcases the wealth of the Wodeyar dynasty."
    },
    {
      id: "mp-3",
      author: "Luca Rossi",
      rating: 4,
      date: "Jul 23, 2026",
      text: "The golden royal howdah and vibrant mosaic flooring are spectacular. Highly recommend visiting during the festive Dasara celebrations."
    }
  ],
  "sanchi-stupa": [
    {
      id: "ss-1",
      author: "Buddhadev Barua",
      rating: 5,
      date: "Aug 26, 2026",
      text: "Commissioned by Emperor Ashoka in the 3rd century BCE, the Great Stupa emanates serenity. The intricate torana gateways tell timeless stories of peace."
    },
    {
      id: "ss-2",
      author: "Pallavi Nigam",
      rating: 5,
      date: "Aug 07, 2026",
      text: "The Ashokan pillar with four lions originated the national emblem of modern India. A sacred cradle of Buddhist philosophy and early stone art."
    },
    {
      id: "ss-3",
      author: "Tenzin Norbu",
      rating: 5,
      date: "Jul 16, 2026",
      text: "A profoundly tranquil hilltop retreat. Meditating near Stupa 1 surrounded by ancient monastery ruins is an uplifting spiritual memory."
    }
  ],
  "rani-ki-vav": [
    {
      id: "rv-1",
      author: "Hemant Solanki",
      rating: 5,
      date: "Aug 30, 2026",
      text: "An inverted underground subterranean temple celebrating water! Over 500 principal sculptures carved on seven terrace levels. The Sheshashayi Vishnu is spellbinding."
    },
    {
      id: "rv-2",
      author: "Bhavna Parekh",
      rating: 5,
      date: "Aug 13, 2026",
      text: "Commissioned by Queen Udayamati in memory of King Bhima I. The precision of Maru-Gurjara stepwell architecture is a masterclass in ancient hydraulic art."
    },
    {
      id: "rv-3",
      author: "Jessica Adams",
      rating: 5,
      date: "Jul 08, 2026",
      text: "Featured on the ₹100 banknote! Seeing it in person reveals layers of ornate stone filigree that survived centuries buried under silt."
    }
  ],
  "charminar": [
    {
      id: "cm-1",
      author: "Mirza Asadullah",
      rating: 5,
      date: "Sep 03, 2026",
      text: "The beating heart of Hyderabad! Built in 1591 by Muhammad Quli Qutb Shah, the four 56-meter minarets with stucco ornamentation stand proud above the bustling Laad Bazaar."
    },
    {
      id: "cm-2",
      author: "Zoya Fathima",
      rating: 4,
      date: "Aug 14, 2026",
      text: "Climbing to the upper balconies for views of Mecca Masjid and shopping for lacquer bangles and pearls nearby makes for a quintessential Hyderabad day."
    },
    {
      id: "cm-3",
      author: "Naveen Reddy",
      rating: 5,
      date: "Jul 21, 2026",
      text: "Brilliantly lit at night. Savoring authentic Irani chai and Osmania biscuits right across the street completes the heritage charm."
    }
  ],
  "victoria-memorial": [
    {
      id: "vm-1",
      author: "Subhashis Ganguly",
      rating: 5,
      date: "Sep 01, 2026",
      text: "Kolkata's crown jewel in white Makrana marble. The bronze Angel of Victory rotating atop the central dome and the extensive royal gallery paintings are majestic."
    },
    {
      id: "vm-2",
      author: "Debarati Roy",
      rating: 5,
      date: "Aug 15, 2026",
      text: "Strolling through the 64-acre gardens along the reflective ponds is pure bliss. A splendid fusion of British and Mughal architectural nuances."
    },
    {
      id: "vm-3",
      author: "Oliver Wright",
      rating: 4,
      date: "Jul 24, 2026",
      text: "Houses rare archival manuscripts, oil paintings, and historical artifacts. The evening projection mapping show is an inspiring journey through Bengal's history."
    }
  ],
  "brihadeshwara-temple": [
    {
      id: "bt-1",
      author: "Rajarajan Sundaram",
      rating: 5,
      date: "Sep 04, 2026",
      text: "The apex of Chola architecture! Built completely of granite with an 80-tonne single-stone Kumbam crowning the 66-meter vimana tower. An engineering miracle that celebrated 1,000 years!"
    },
    {
      id: "bt-2",
      author: "Sowmya Natarajan",
      rating: 5,
      date: "Aug 19, 2026",
      text: "The massive monolithic Nandi bull carved from a single rock and the ancient Chola frescos inside the corridor are awe-inspiring."
    },
    {
      id: "bt-3",
      author: "Frederic Moreau",
      rating: 5,
      date: "Jul 19, 2026",
      text: "The symmetry, scale, and acoustic design of the temple courtyard make it one of the absolute greatest architectural achievements in Asia."
    }
  ],
  "mahabalipuram": [
    {
      id: "mb-1",
      author: "Venkatesan Pillai",
      rating: 5,
      date: "Aug 29, 2026",
      text: "Arjuna's Penance is the largest open-air rock relief in the world! The Shore Temple standing resilient against Bay of Bengal waves for 1,300 years is breathtaking."
    },
    {
      id: "mb-2",
      author: "Divya Balasubramanian",
      rating: 5,
      date: "Aug 06, 2026",
      text: "The monolithic Pancha Rathas carved from single boulders resemble life-size temple chariots. Krishna's Butter Ball defying gravity on the slope is a delight."
    },
    {
      id: "mb-3",
      author: "Chloe Martin",
      rating: 5,
      date: "Jul 14, 2026",
      text: "Sea breeze, ancient Pallava maritime history, and sculptors actively carving granite along every lane. A magical UNESCO world heritage destination."
    }
  ],
  "gateway-of-india": [
    {
      id: "gi-1",
      author: "Aditya Merchant",
      rating: 5,
      date: "Sep 05, 2026",
      text: "Mumbai's most enduring monument. Standing at Apollo Bunder overlooking the Arabian Sea with the iconic Taj Mahal Palace hotel beside it is pure nostalgia."
    },
    {
      id: "gi-2",
      author: "Natasha Cooper",
      rating: 4,
      date: "Aug 22, 2026",
      text: "The yellow basalt stone and 16th-century Gujarati architectural filigree work blend beautifully with European triumphal arch design. Great ferries to Elephanta Caves."
    },
    {
      id: "gi-3",
      author: "Farhan Qureshi",
      rating: 5,
      date: "Jul 31, 2026",
      text: "Cool sea breeze, feeding pigeons, street photographers, and historical significance where the last British troops departed India in 1948."
    }
  ]
};

const STORAGE_KEY = 'virasatai_monument_reviews';

/**
 * Helper to fetch local storage submissions
 */
function getLocalSubmissions() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch (err) {
    console.warn('Error reading reviews from localStorage:', err);
    return {};
  }
}

/**
 * Save user submissions to local storage
 */
function saveLocalSubmissions(data) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  } catch (err) {
    console.warn('Error saving reviews to localStorage:', err);
  }
}

/**
 * Retrieve all reviews for a monument (merges local submissions + seed reviews)
 */
export function getMonumentReviews(siteId) {
  const local = getLocalSubmissions();
  const userReviews = local[siteId] || [];
  const seeds = SEED_REVIEWS[siteId] || [];
  // Return user reviews first (newest submissions at top) followed by baseline seeds
  return [...userReviews, ...seeds];
}

/**
 * Calculate dynamic rating statistics for a monument
 */
export function getMonumentRatingStats(siteId) {
  const reviews = getMonumentReviews(siteId);
  const total = reviews.length;

  if (total === 0) {
    return {
      average: '5.0',
      total: 0,
      counts: { 5: 0, 4: 0, 3: 0, 2: 0, 1: 0 },
      percentages: { 5: 0, 4: 0, 3: 0, 2: 0, 1: 0 }
    };
  }

  const counts = { 5: 0, 4: 0, 3: 0, 2: 0, 1: 0 };
  let sum = 0;

  reviews.forEach(r => {
    const rating = Math.min(5, Math.max(1, parseInt(r.rating) || 5));
    counts[rating] = (counts[rating] || 0) + 1;
    sum += rating;
  });

  const average = (sum / total).toFixed(1);
  const percentages = {};
  for (let s = 1; s <= 5; s++) {
    percentages[s] = Math.round((counts[s] / total) * 100);
  }

  return {
    average,
    total,
    counts,
    percentages
  };
}

/**
 * Save a new user review for a monument
 */
export function saveMonumentReview(siteId, { author, rating, text, date }) {
  const local = getLocalSubmissions();
  if (!local[siteId]) {
    local[siteId] = [];
  }

  const formattedDate = date || new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: '2-digit',
    year: 'numeric'
  }).format(new Date());

  const newReview = {
    id: 'usr-' + Date.now() + '-' + Math.floor(Math.random() * 1000),
    author: (author && author.trim()) ? author.trim() : 'Heritage Explorer',
    rating: Math.min(5, Math.max(1, parseInt(rating) || 5)),
    date: formattedDate,
    text: (text && text.trim()) ? text.trim() : '',
    siteId,
    verified: true,
    isLocalUser: true
  };

  local[siteId].unshift(newReview);
  saveLocalSubmissions(local);

  return {
    newReview,
    allReviews: getMonumentReviews(siteId),
    stats: getMonumentRatingStats(siteId)
  };
}
