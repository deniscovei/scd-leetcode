import React from 'react';
import ReactMarkdown from 'react-markdown';
import './ProblemDescription.css';

interface ProblemDescriptionProps {
    title?: string;
    description: string;
    examples?: string[];
}

const ProblemDescription: React.FC<ProblemDescriptionProps> = ({ title, description, examples = [] }) => {
    return (
        <div className="problem-description">
            {title && <h2>{title}</h2>}
            <div className="problem-description-content">
                <ReactMarkdown>{description}</ReactMarkdown>
            </div>
            {examples && examples.length > 0 && (
                <>
                    <h3>Examples:</h3>
                    <ul>
                        {examples.map((example, index) => (
                            <li key={index}>{example}</li>
                        ))}
                    </ul>
                </>
            )}
        </div>
    );
};


export default ProblemDescription;