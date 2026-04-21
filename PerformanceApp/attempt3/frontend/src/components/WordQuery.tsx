import { FormEvent, useState } from "react";

interface WordQueryProps {
  disabled: boolean;
  isSearching: boolean;
  onSearch: (word: string) => Promise<void>;
}

function WordQuery({ disabled, isSearching, onSearch }: WordQueryProps) {
  const [word, setWord] = useState("");

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!word.trim()) {
      return;
    }

    await onSearch(word);
  };

  return (
    <form className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm" onSubmit={onSubmit}>
      <h2 className="text-lg font-semibold">Count Word Occurrences</h2>
      <input
        className="mt-3 block w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 disabled:cursor-not-allowed disabled:bg-slate-100"
        type="text"
        value={word}
        onChange={(event) => setWord(event.target.value)}
        placeholder="Enter a single word"
        disabled={disabled}
      />
      <button
        className="mt-3 inline-flex w-fit items-center rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-400"
        type="submit"
        disabled={disabled || isSearching || !word.trim()}
      >
        {isSearching ? "Searching..." : "Count"}
      </button>
    </form>
  );
}

export default WordQuery;
