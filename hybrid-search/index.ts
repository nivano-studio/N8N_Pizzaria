import { createClient } from "npm:@supabase/supabase-js@2";
import OpenAI from "npm:openai";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

Deno.serve(async (req: Request) => {
  // Responde às verificações CORS.
  if (req.method === "OPTIONS") {
    return new Response("ok", {
      headers: corsHeaders,
    });
  }

  if (req.method !== "POST") {
    return new Response(
      JSON.stringify({
        error: "Método não permitido. Utilize POST.",
      }),
      {
        status: 405,
        headers: {
          ...corsHeaders,
          "Content-Type": "application/json",
        },
      },
    );
  }

  try {
    const body = await req.json();
    const query =
      typeof body?.query === "string"
        ? body.query.trim()
        : "";

    if (!query) {
      return new Response(
        JSON.stringify({
          error: 'Envie uma pergunta no campo "query".',
          exemplo: {
            query: "Quais produtos estão disponíveis?",
          },
        }),
        {
          status: 400,
          headers: {
            ...corsHeaders,
            "Content-Type": "application/json",
          },
        },
      );
    }

    const supabaseUrl = Deno.env.get("SUPABASE_URL");
    const supabaseServiceRoleKey = Deno.env.get(
      "SUPABASE_SERVICE_ROLE_KEY",
    );
    const openaiApiKey = Deno.env.get("OPENAI_API_KEY");

    if (!supabaseUrl) {
      throw new Error("A variável SUPABASE_URL não foi encontrada.");
    }

    if (!supabaseServiceRoleKey) {
      throw new Error(
        "A variável SUPABASE_SERVICE_ROLE_KEY não foi encontrada.",
      );
    }

    if (!openaiApiKey) {
      throw new Error(
        "A variável OPENAI_API_KEY não foi configurada.",
      );
    }

    // Gera o embedding da pergunta.
    const openai = new OpenAI({
      apiKey: openaiApiKey,
    });

    const embeddingResponse = await openai.embeddings.create({
      model: "text-embedding-3-large",
      input: query,
      dimensions: 1536,
    });

    const embedding = embeddingResponse.data[0]?.embedding;

    if (!embedding) {
      throw new Error("A OpenAI não retornou o embedding.");
    }

    // Conecta ao Supabase pelo ambiente seguro da Edge Function.
    const supabase = createClient(
      supabaseUrl,
      supabaseServiceRoleKey,
      {
        auth: {
          persistSession: false,
          autoRefreshToken: false,
        },
      },
    );

    // Executa a função SQL hybrid_search.
    const { data, error } = await supabase.rpc(
      "hybrid_search",
      {
        query_text: query,
        query_embedding: embedding,
        match_count: 10,
      },
    );

    if (error) {
      throw new Error(
        `Erro ao executar hybrid_search: ${error.message}`,
      );
    }

    return new Response(
      JSON.stringify({
        success: true,
        query,
        total: data?.length ?? 0,
        documents: data ?? [],
      }),
      {
        status: 200,
        headers: {
          ...corsHeaders,
          "Content-Type": "application/json",
        },
      },
    );
  } catch (error) {
    const message =
      error instanceof Error
        ? error.message
        : "Erro interno desconhecido.";

    console.error("Erro na função hybrid-search:", error);

    return new Response(
      JSON.stringify({
        success: false,
        error: message,
      }),
      {
        status: 500,
        headers: {
          ...corsHeaders,
          "Content-Type": "application/json",
        },
      },
    );
  }
});